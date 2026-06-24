use std::error::Error;
use std::fs;
use std::path::PathBuf;
use std::process;
use clap::{Parser, Subcommand, Args};
use users::{get_uid_by_name, get_username_by_uid, get_gid_by_name, get_groupname_by_gid};
use nix::unistd::Uid;
use nix::unistd::Gid;

#[derive(Parser)]
struct Opts {
    #[clap(long, value_parser)]
    owner: Option<String>,
    #[clap(long, value_parser)]
    path: String,
}

fn main() -> Result<(), Box<dyn Error>> {
    let opts = Opts::parse();
    if let Some(owner) = opts.owner {
        let parts: Vec<&str> = owner.split(':').collect();
        let uid: Option<Uid>;
        let gid: Option<Gid>;
        match parts.len() {
            1 => {
                if parts[0].parse::<u32>().is_ok() {
                    uid = Some(Uid::from_raw(parts[0].parse::<u32>().unwrap()));
                    gid = None;
                } else {
                    uid = Some(get_uid_by_name(parts[0]).ok_or("Invalid username")?);
                    gid = None;
                }
            }
            2 => {
                if parts[0].parse::<u32>().is_ok() {
                    uid = Some(Uid::from_raw(parts[0].parse::<u32>().unwrap()));
                } else {
                    uid = Some(get_uid_by_name(parts[0]).ok_or("Invalid username")?);
                }
                if parts[1].parse::<u32>().is_ok() {
                    gid = Some(Gid::from_raw(parts[1].parse::<u32>().unwrap()));
                } else {
                    gid = Some(get_gid_by_name(parts[1]).ok_or("Invalid groupname")?);
                }
            }
            _ => return Err("Invalid owner format".into()),
        }
        let path = PathBuf::from(opts.path);
        for entry in fs::read_dir(path)? {
            let entry = entry?;
            let metadata = entry.metadata()?;
            if metadata.is_file() {
                let file_uid = metadata.uid();
                let file_gid = metadata.gid();
                if let Some(uid) = uid {
                    if file_uid != uid {
                        continue;
                    }
                }
                if let Some(gid) = gid {
                    if file_gid != gid {
                        continue;
                    }
                }
                println!("{}", entry.path().file_name().unwrap().to_str().unwrap());
            }
        }
    } else {
        eprintln!("Please provide --owner option");
        process::exit(1);
    }
    Ok(())
}