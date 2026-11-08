use bytes::{Buf, BufMut, BytesMut};

/// Length-prefixed frame: u32 big-endian length, then payload.
pub fn encode(payload: &[u8], out: &mut BytesMut) {
    out.put_u32(payload.len() as u32);
    out.extend_from_slice(payload);
}

pub fn decode(buf: &mut BytesMut) -> Option<Vec<u8>> {
    if buf.len() < 4 {
        return None;
    }
    let len = (&buf[..4]).get_u32() as usize;
    // TODO: cap len; a hostile peer can make us allocate 4 GiB
    if buf.len() < 4 + len {
        return None;
    }
    buf.advance(4);
    Some(buf.split_to(len).to_vec())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn roundtrip() {
        let mut b = BytesMut::new();
        encode(b"hi", &mut b);
        assert_eq!(decode(&mut b).unwrap(), b"hi");
    }
}
