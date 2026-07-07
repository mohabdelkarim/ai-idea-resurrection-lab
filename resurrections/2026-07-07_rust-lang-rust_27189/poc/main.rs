use std::env;
use std::process;
use rustc_errors::{ErrorGuaranteed, FatalError};
use rustc_interface::interface;
use rustc_middle::ty::TyCtxt;
use rustc_session::{Session, CompilerOptions};
use rustc_span::edition::Edition;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <file>", args[0]);
        process::exit(1);
    }
    let file = &args[1];
    let mut opts = CompilerOptions::default();
    opts.fatal_on_first_error = true;
    let sess = Session::new(opts, "rustc");
    let result = interface::run_compiler(&sess, file, |tcx| {
        let mut errors = 0;
        tcx.sess.diagnostics().errors(|err| {
            if err.is_fatal() {
                errors += 1;
                if tcx.sess.opts.fatal_on_first_error {
                    tcx.sess.fatal("fatal error occurred");
                }
            }
        });
        if errors > 0 {
            return Err(ErrorGuaranteed::new());
        }
        Ok(())
    });
    if let Err(_) = result {
        process::exit(1);
    }
}