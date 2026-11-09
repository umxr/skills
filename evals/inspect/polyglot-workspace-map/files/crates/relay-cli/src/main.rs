use clap::Parser;
use relay_core::Router;

#[derive(Parser)]
struct Args {
    #[arg(long, default_value = "0.0.0.0:7000")]
    listen: String,
}

#[tokio::main]
async fn main() {
    let args = Args::parse();
    let _router = Router::new();
    println!("relay listening on {}", args.listen);
    // accept loop lives in relay-core::forwarder (not yet extracted)
}
