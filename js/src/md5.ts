// RFC 1321 MD5 over raw bytes, returning the Base64 of the 16-byte digest — the
// value the upload target expects as the Content-MD5 header on a direct-upload
// PUT. Web Crypto has no MD5, so direct upload needs this pure implementation to
// run in browsers as well as Node.

const SHIFTS = [
  7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
  5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
  4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
  6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
];

const K = Array.from({ length: 64 }, (_v, i) =>
  Math.floor(Math.abs(Math.sin(i + 1)) * 4294967296),
);

function add32(a: number, b: number): number {
  return (a + b) & 0xffffffff;
}

function rotl(value: number, bits: number): number {
  return (value << bits) | (value >>> (32 - bits));
}

function md5Bytes(input: Uint8Array): Uint8Array {
  const withOne = input.length + 1;
  const totalLen = withOne + ((56 - (withOne % 64) + 64) % 64) + 8;
  const msg = new Uint8Array(totalLen);
  msg.set(input);
  msg[input.length] = 0x80;

  const view = new DataView(msg.buffer);
  const bitLen = input.length * 8;
  view.setUint32(totalLen - 8, bitLen >>> 0, true);
  view.setUint32(totalLen - 4, Math.floor(bitLen / 0x100000000) >>> 0, true);

  let a0 = 0x67452301;
  let b0 = 0xefcdab89;
  let c0 = 0x98badcfe;
  let d0 = 0x10325476;

  const m = new Int32Array(16);
  for (let offset = 0; offset < totalLen; offset += 64) {
    for (let j = 0; j < 16; j += 1) {
      m[j] = view.getUint32(offset + j * 4, true);
    }

    let a = a0;
    let b = b0;
    let c = c0;
    let d = d0;

    for (let i = 0; i < 64; i += 1) {
      let f: number;
      let g: number;
      if (i < 16) {
        f = (b & c) | (~b & d);
        g = i;
      } else if (i < 32) {
        f = (d & b) | (~d & c);
        g = (5 * i + 1) % 16;
      } else if (i < 48) {
        f = b ^ c ^ d;
        g = (3 * i + 5) % 16;
      } else {
        f = c ^ (b | ~d);
        g = (7 * i) % 16;
      }

      f = add32(add32(f, a), add32(K[i], m[g]));
      a = d;
      d = c;
      c = b;
      b = add32(b, rotl(f, SHIFTS[i]));
    }

    a0 = add32(a0, a);
    b0 = add32(b0, b);
    c0 = add32(c0, c);
    d0 = add32(d0, d);
  }

  const out = new Uint8Array(16);
  const outView = new DataView(out.buffer);
  outView.setUint32(0, a0 >>> 0, true);
  outView.setUint32(4, b0 >>> 0, true);
  outView.setUint32(8, c0 >>> 0, true);
  outView.setUint32(12, d0 >>> 0, true);
  return out;
}

const BASE64_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

function bytesToBase64(bytes: Uint8Array): string {
  let out = '';
  for (let i = 0; i < bytes.length; i += 3) {
    const b0 = bytes[i];
    const b1 = i + 1 < bytes.length ? bytes[i + 1] : 0;
    const b2 = i + 2 < bytes.length ? bytes[i + 2] : 0;
    out += BASE64_CHARS[b0 >> 2];
    out += BASE64_CHARS[((b0 & 3) << 4) | (b1 >> 4)];
    out += i + 1 < bytes.length ? BASE64_CHARS[((b1 & 15) << 2) | (b2 >> 6)] : '=';
    out += i + 2 < bytes.length ? BASE64_CHARS[b2 & 63] : '=';
  }
  return out;
}

export function md5Base64(bytes: Uint8Array): string {
  return bytesToBase64(md5Bytes(bytes));
}
