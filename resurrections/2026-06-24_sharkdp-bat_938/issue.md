# Ubuntu install error when rg is installed also

**Repository:** [sharkdp/bat](https://github.com/sharkdp/bat)
**Issue:** [sharkdp/bat#938](https://github.com/sharkdp/bat/issues/938)
**Reactions:** 50 👍
**Created:** 2020-04-23T09:00:06Z
**Last Activity:** 2022-04-22T15:10:58Z
**Labels:** bug, packaging/tooling

---

## Original Description

Running Ubuntu 20.04:
```
$ sudo apt install bat ripgrep
Reading package lists... Done
Building dependency tree       
Reading state information... Done
The following additional packages will be installed:
  libgit2-28 libhttp-parser2.9 libmbedcrypto3 libmbedtls12 libmbedx509-0
  libssh2-1
The following NEW packages will be installed:
  bat libgit2-28 libhttp-parser2.9 libmbedcrypto3 libmbedtls12 libmbedx509-0
  libssh2-1 ripgrep
0 to upgrade, 8 to newly install, 0 to remove and 1 not to upgrade.
Need to get 1,228 kB/3,577 kB of archives.
After this operation, 11.1 MB of additional disk space will be used.
Do you want to continue? [Y/n] Y
Get:1 http://au.archive.ubuntu.com/ubuntu focal/universe amd64 ripgrep amd64 11.0.2-1build1 [1,228 kB]
Fetched 1,228 kB in 0s (2,731 kB/s)
INFO Requesting to save current system state      
Successfully saved as "autozsys_j4dqft"
Selecting previously unselected package libhttp-parser2.9:amd64.
(Reading database ... 225178 files and directories currently installed.)
Preparing to unpack .../0-libhttp-parser2.9_2.9.2-2_amd64.deb ...
Unpacking libhttp-parser2.9:amd64 (2.9.2-2) ...
Selecting previously unselected package libmbedcrypto3:amd64.
Preparing to unpack .../1-libmbedcrypto3_2.16.4-1ubuntu2_amd64.deb ...
Unpacking libmbedcrypto3:amd64 (2.16.4-1ubuntu2) ...
Selecting previously unselected package libmbedx509-0:amd64.
Preparing to unpack .../2-libmbedx509-0_2.16.4-1ubuntu2_amd64.deb ...
Unpacking libmbedx509-0:amd64 (2.16.4-1ubuntu2) ...
Selecting previously unselected package libmbedtls12:amd64.
Preparing to unpack .../3-libmbedtls12_2.16.4-1ubuntu2_amd64.deb ...
Unpacking libmbedtls12:amd64 (2.16.4-1ubuntu2) ...
Selecting previously unselected package libssh2-1:amd64.
Preparing to unpack .../4-libssh2-1_1.8.0-2.1build1_amd64.deb ...
Unpacking libssh2-1:amd64 (1.8.0-2.1build1) ...
Selecting previously unselected package libgit2-28:amd64.
Preparing to unpack .../5-libgit2-28_0.28.4+dfsg.1-2_amd64.deb ...
Unpacking libgit2-28:amd64 (0.28.4+dfsg.1-2) ...
Preparing to unpack .../6-bat_0.12.1-1build1_amd64.deb ...
Unpacking bat (0.12.1-1build1) ...
Selecting previously unselected package ripgrep.
Preparing to unpack .../7-ripgrep_11.0.2-1build1_amd64.deb ...
Unpacking ripgrep (11.0.2-1build1) ...
dpkg: error processing archive /tmp/apt-dpkg-install-8eoEcZ/7-ripgrep_11.0.2-1bu
ild1_amd64.deb (--unpack):
 trying to overwrite '/usr/.crates2.json', which is also in package bat 0.12.1-1
build1
dpkg-deb: error: paste subprocess was killed by signal (Broken pipe)
Errors were encountered while processing:
 /tmp/apt-dpkg-install-8eoEcZ/7-ripgrep_11.0.2-1build1_amd64.deb
INFO Updating GRUB menu                           
E: Sub-process /usr/bin/dpkg returned an error code (1)
```

---

*Resurrected by Resurrection Bot 🧬*
