# idna 3.0 version package conflict

**Repository:** [psf/requests](https://github.com/psf/requests)
**Issue:** [psf/requests#5710](https://github.com/psf/requests/issues/5710)
**Reactions:** 88 👍
**Created:** 2021-01-01T12:29:46Z
**Last Activity:** 2021-10-07T20:00:26Z
**Labels:** 

---

## Original Description

idna released version 3.0 but requests has a dependency on idna<3, this makes it impossible to keep up to date on both packages.

## Expected Result
I want to be able to install the latest idna package alongside the latest requests package


## Actual Result

```
ERROR: Cannot install -r requirements.txt (line 12) and idna==3.0 because these package versions have conflicting dependencies.

The conflict is caused by:

    The user requested idna==3.0

    requests 2.25.1 depends on idna<3 and >=2.5
```

## Reproduction Steps

try to run `pip install` on a requirements.txt file with 
```
requests==2.25.1
idna==3.0
```

## System Information

multiple Python versions (3.6 up to 3.9) running on Docker containers inside Drone CI/CD 

---

*Resurrected by Resurrection Bot 🧬*
