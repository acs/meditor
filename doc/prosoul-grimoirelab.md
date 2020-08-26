# Using Prosoul with GrimoireLab

### Start Prosoul, Elasticsearch and Kibiter using docker

```
p0tt3r@wand ~/dev/prosoul/docker $ docker-compose up -d
Starting docker_elasticsearch_1 ... done
Starting docker_kibiter_1       ... done
Starting docker_prosoul_1       ... done
```

The three services will be available at their respective ports.
- Elasticsearch at https://localhost:9200/
- Kibiter at http://localhost:5601/
- Prosoul at http://localhost:8000/

Let's perform an assessment for a few grimoirelab projects using the `gitqm` and `githubqm` backends and the Developer Quality Model (for GrimoireLab).
 
### Load GrimoireLab Data

You need to setup [SirMordred](https://github.com/chaoss/grimoirelab-sirmordred) project. You can use the [Getting-Started.md](https://github.com/chaoss/grimoirelab-sirmordred/blob/master/Getting-Started.md#getting-started-) guide and omit the `Getting the containers` section as the Elasticsearch and Kibiter are already available.

Now that you have the project configured in the PyCharm, we can execute micro-mordred/sirmordred. All you need to define the setup.cfg and projects.json with the required configurations and execute the backends.

Let's use micro-mordred for this purpose.

projects.json
```
{
    "GrimoireLab": {
        "gitqm": [
            "https://github.com/chaoss/grimoirelab-elk" ,
            "https://github.com/chaoss/grimoirelab-kidash" ,
            "https://github.com/chaoss/grimoirelab-sirmordred" ,
            "https://github.com/chaoss/grimoirelab-perceval" ,
            "https://github.com/chaoss/grimoirelab-sortinghat"
        ] ,
        "githubqm:issue": [
            "https://github.com/chaoss/grimoirelab-elk" ,
            "https://github.com/chaoss/grimoirelab-kidash" ,
            "https://github.com/chaoss/grimoirelab-sirmordred" ,
            "https://github.com/chaoss/grimoirelab-perceval" ,
            "https://github.com/chaoss/grimoirelab-sortinghat"
        ]
    }
}
```

setup.cfg
```
[gitqm]
raw_index = grimoirelab_gitqm_raw
enriched_index = grimoirelab_gitqm_enriched
category = commit

[githubqm:issue]
raw_index = grimoirelab_githubqm_issues_raw
enriched_index = grimoirelab_githubqm_issues_enriched
api-token = xxxx
sleep-for-rate = true
sleep-time = 300
category = issue
no-archive = true
```
You can find all the configurations here, link.

Now, execute the raw and enrich tasks of micro-mordred.
```
micro.py --raw --enrich --cfg ./setup.cfg --backends gitqm githubqm:issue
```

Setup alias for all the enriched indices.
```
POST /_aliases
{
  "actions": [
    {
      "add": {
        "indices": [
          "grimoirelab_gitqm_enriched",
          "grimoirelab_githubqm_issues_enriched"
        ],
        "alias": "all_qm_data"
      }
    }
  ]
}
```

Now, you have all the required enriched data in `qm-enriched-data` index which is needed for the assessement and visualization using Prosoul.

### Import the QualityModel

Import the [Developer Quality Model](https://github.com/Bitergia/prosoul/blob/master/django_prosoul/prosoul/data/developer_model_grimoirelab.json) using prosoul web editor.

### Load the Metrics Data

Login with the admin credentials and go to the admin panel, `Prosoul Site Administration` and click on `Metric datas`. You have to entry the metric items data by clicking on the `ADD METRIC DATA` button. You can add the metric data by filling out the web form using the `metric_name`.

- Description: Number of Commits
- Implementation: Number of Commits

Similarly, you have to add all the metrics data which you use while making a Quality Model.

### Create the Assessment

The next step is to create the assessment using prosoul assessment web form.

- Quality Model: Developer Quality Model
- Elasticsearch URL: https://localhost:9200/
- Index with metrics data: all_qm_data

Click on `Create` and the assessment will be completed in a while.

After the assessment is completed, you can view the results using the prosoul web interface.

### Import the Dashboard

Setup alias for all the qm results indices.
```
POST /_aliases
{
  "actions": [
    {
      "add": {
        "indices": [
          "all_qm_data_null_scores",
          "all_qm_data_null_scores_by_quarters",
          "all_qm_data_scores",
          "all_qm_data_scores_by_quarters"
        ],
        "alias": "all_qm_data_results"
      }
    }
  ]
}
```

Import the dashboard from the sigils repository.
```
p0tt3r@wand ~ $ kidash -g -e https://admin:admin@localhost:9200 --import ~/dev/sources/grimoirelab-sigils/json/qm-dashboard.json
```

After importing the dashboard, you can view the results in the dashboard and edit the visualizations as per your need.

