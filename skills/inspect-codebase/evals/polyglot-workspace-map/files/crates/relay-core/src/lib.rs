//! Core message relay: framing, routing table and the async forwarder.
pub mod frame;
pub mod router;

pub use router::Router;
