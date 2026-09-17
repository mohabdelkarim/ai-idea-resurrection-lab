# Load scrape configs from multiple files

**Repository:** [prometheus/prometheus](https://github.com/prometheus/prometheus)
**Issue:** [prometheus/prometheus#8543](https://github.com/prometheus/prometheus/issues/8543)
**Reactions:** 59 👍
**Created:** 2021-02-25T21:13:10Z
**Last Activity:** 2023-09-16T23:18:35Z
**Labels:** priority/Pmaybe, component/scraping, kind/feature

---

## Original Description

This issue is about providing the ability to split Prometheus scrape configs into multiple files.

Design doc: https://docs.google.com/document/d/1bSehbL_Rzx9_guVgISmara-Ft_FB57q_YxEZtwxE3C8/edit#heading=h.bupciudrwmna


Add a new parameter `scrape_config_files: [ - <filepath_glob> ... ]`.

The files in the scrape_config_files are read, and may contain one or multiple files. The filenames can contain globs (scrape_configs.d/*.yml). Relative paths are relative to the main config file.

The files are re-read on every reload. Wrong scrape configs make the reload fail, and scrape configs as applied before apply. Errors reading scrape configs prevent Prometheus to start.

Scrape config names must be unique between prometheus.yml and imported files, otherwise reload/start fail.

Scrape configs are never merged together.


Exemple scrape config file:

Prometheus.yml

```
global: 
   scrape_interval: 10s
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']
scrape_config_files:
  - blackbox.yml
```

blackbox.yml

```
scrape_configs:
 - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - http://prometheus.io
        - https://prometheus.io
        - http://example.com:8080
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 127.0.0.1:9115  # The blackbox exporter's real hostname:port.
```

---

*Resurrected by Resurrection Bot 🧬*
