# frozen_string_literal: true

require "spec_helper"
require "tempfile"

RSpec.describe RunApi::Core::Uploads do
  let(:http) { instance_double(RunApi::Core::HttpClient) }
  let(:uploads) { described_class.new(http) }
  let(:upload) do
    {"id" => "upload_123", "object" => "upload", "bytes" => 3, "created_at" => 1,
     "filename" => "data.bin", "purpose" => "user_data", "status" => "pending", "expires_at" => 2}
  end

  it "supports create, add-part, complete, and cancel" do
    tempfile = Tempfile.new("part.bin")
    tempfile.write("abc")
    tempfile.close
    expect(http).to receive(:request).with(
      :post, "/v1/uploads",
      body: {bytes: 3, filename: "data.bin", mime_type: "application/octet-stream", purpose: "user_data"}
    ).and_return(upload)
    expect(http).to receive(:request).with(
      :post, "/v1/uploads/upload_123/parts",
      body: instance_of(RunApi::Core::MultipartBody)
    ).and_return({"id" => "part_123", "object" => "upload.part", "created_at" => 1, "upload_id" => "upload_123"})
    expect(http).to receive(:request).with(
      :post, "/v1/uploads/upload_123/complete", body: {part_ids: ["part_123"]}
    ).and_return(upload.merge("status" => "completed"))
    expect(http).to receive(:request).with(
      :post, "/v1/uploads/upload_123/cancel", body: {}
    ).and_return(upload.merge("status" => "cancelled"))

    expect(uploads.create(bytes: 3, filename: "data.bin", mime_type: "application/octet-stream").id).to eq("upload_123")
    expect(uploads.add_part("upload_123", data: tempfile.path).id).to eq("part_123")
    expect(uploads.complete("upload_123", part_ids: ["part_123"]).status).to eq("completed")
    expect(uploads.cancel("upload_123").status).to eq("cancelled")
  ensure
    tempfile.unlink
  end
end
