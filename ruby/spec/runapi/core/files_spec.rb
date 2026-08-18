# frozen_string_literal: true

require "spec_helper"
require "digest"
require "stringio"
require "tempfile"

RSpec.describe RunApi::Core::Files do
  let(:http) { instance_double(RunApi::Core::HttpClient) }
  let(:files) { described_class.new(http) }
  let(:response) do
    {
      "file_name" => "image.png",
      "url" => "https://file.runapi.ai/temp/image.png",
      "size_bytes" => 204800,
      "mime_type" => "image/png",
      "created_at" => "2026-06-08T10:30:00Z",
      "expires_at" => "2026-06-08T11:30:00Z"
    }
  end

  describe "#create" do
    it "can be required via runapi/core" do
      load_path = [
        File.expand_path("../../../lib", __dir__)
      ].join(File::PATH_SEPARATOR)

      output = IO.popen(
        {"RUBYLIB" => load_path},
        [RbConfig.ruby, "-e", "require 'runapi/core'; puts RunApi::Core::Files.name"],
        err: [:child, :out],
        &:read
      )

      expect($?).to be_success
      expect(output).to include("RunApi::Core::Files")
    end

    it "POSTs URL source JSON to the file create endpoint" do
      expect(http).to receive(:request)
        .with(:post, "/api/v1/files", body: {
          source: {type: "url", url: "https://cdn.runapi.ai/public/samples/mask.png"},
          file_name: "image.png"
        })
        .and_return(response)

      result = files.create(
        source: {type: "url", url: "https://cdn.runapi.ai/public/samples/mask.png"},
        file_name: "image.png"
      )

      expect(result).to be_a(RunApi::Core::Files::UploadResponse)
      expect(result.url).to eq("https://file.runapi.ai/temp/image.png")
      expect(result.expires_at).to eq("2026-06-08T11:30:00Z")
    end

    it "uploads local files directly via prepare, PUT, then confirm" do
      tempfile = Tempfile.new(["image", ".png"])
      tempfile.write("png")
      tempfile.close

      prepared = {
        "signed_id" => "signed-blob-id",
        "upload_url" => "https://file.runapi.ai/temp/user-uploads/key",
        "headers" => {"Content-Type" => "application/octet-stream", "Content-MD5" => Digest::MD5.base64digest("png")}
      }

      # prepare: declares the file, never sends bytes through the API
      expect(http).to receive(:request)
        .with(:post, "/api/v1/files/prepare", body: {
          filename: "image.png",
          byte_size: 3,
          checksum: Digest::MD5.base64digest("png")
        }, options: nil)
        .and_return(prepared)

      # PUT: bytes go straight to the issued upload URL with its headers
      expect(http).to receive(:upload)
        .with("https://file.runapi.ai/temp/user-uploads/key", headers: prepared["headers"], body: "png")

      # confirm: resolves the final resource
      expect(http).to receive(:request)
        .with(:post, "/api/v1/files/confirm", body: {signed_id: "signed-blob-id"})
        .and_return(response)

      result = files.create(file: tempfile.path, file_name: "image.png")
      expect(result).to be_a(RunApi::Core::Files::UploadResponse)
      expect(result.file_name).to eq("image.png")
    ensure
      tempfile.unlink
    end

    it "rejects in-memory IO objects with a clear error" do
      expect(http).not_to receive(:request)

      expect { files.create(file: StringIO.new("png"), file_name: "image.png") }
        .to raise_error(ArgumentError, "file must be a file path or respond to :path")
    end

    it "rejects missing upload source before sending a request" do
      expect(http).not_to receive(:request)

      expect { files.create }.to raise_error(ArgumentError, /Exactly one source/)
    end

    it "rejects multiple upload sources before sending a request" do
      expect(http).not_to receive(:request)

      expect do
        files.create(
          file: "image.png",
          source: {type: "url", url: "https://cdn.runapi.ai/public/samples/mask.png"}
        )
      end.to raise_error(ArgumentError, /Exactly one source/)
    end
  end

  describe "OpenAI-compatible File lifecycle" do
    let(:file_object) do
      {"id" => "file_123", "object" => "file", "bytes" => 3, "created_at" => 1,
       "filename" => "input.bin", "purpose" => "user_data"}
    end

    it "creates, lists, retrieves, downloads, and deletes Files" do
      tempfile = Tempfile.new("input.bin")
      tempfile.binmode
      tempfile.write("\x00\xff\x01".b)
      tempfile.close
      expect(http).to receive(:request).with(
        :post, "/v1/files",
        body: instance_of(RunApi::Core::MultipartBody)
      ).and_return(file_object)
      expect(http).to receive(:request).with(:get, "/v1/files?limit=1&order=asc")
        .and_return({"object" => "list", "data" => [], "has_more" => false})
      expect(http).to receive(:request).with(:get, "/v1/files/file_123").and_return(file_object)
      expect(http).to receive(:request).with(
        :get, "/v1/files/file_123/content", options: nil, raw: true
      ).and_return("\x00\xff\x01".b)
      expect(http).to receive(:request).with(:delete, "/v1/files/file_123")
        .and_return({"id" => "file_123", "object" => "file", "deleted" => true})

      expect(files.create_file(file: tempfile.path).id).to eq("file_123")
      expect(files.list(limit: 1, order: "asc").has_more).to be(false)
      expect(files.retrieve("file_123").filename).to eq("input.bin")
      expect(files.content("file_123")).to eq("\x00\xff\x01".b)
      expect(files.delete_file("file_123").deleted).to be(true)
    ensure
      tempfile.unlink
    end
  end
end
