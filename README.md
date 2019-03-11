drone-spotinst-esg-scaler
====================

* Author: `Florian Dambrine <florian@gumgum.com>`

Adjust the capacity of a Spotinst ESG

# :notebook: Usage

* At least one example of usage

```yaml
---

pipeline:
    esg_scale:
        image: gumgum-docker.jfrog.io/spotinst-esg-scaler
        account_id: act-1234abcd
        esg_name: va-web--stage
        adjustement: +1
        secrets:
          - source: spotinst_api_token
            target: api_token
```

---

# :gear: Parameter Reference

* `account_id`

The Spotinst account ID in which the ESG is running in (_act-xxx_)

* `api_token`

Spotinst API token

* `adjustement_type` _(optional default to `count`)_

Defines how to scale the ESG:
  * `count` will add `adjustement` to the current size
  * `double` will double the size of the ESG
  * `half` will add half the size of the ESG


* `adjustement` _(optional default to `+1`)_

Defines by how much the group should be scaled up (only valid if `adjustement_type: count`)

---

# :beginner: Development

* Run the plugin directly from a built Docker image:

```bash
docker run -i \
           -v $(pwd)/plugin:/opt/drone/plugin \
           -v ~/.aws:/root/.aws \
           -e API_TOKEN=$SPOTINST_API_TOKEN \
           -e PLUGIN_ACCOUNT_ID=act-1234abcd \
           -e PLUGIN_ESG_NAME=va-web--stage \
           gumgum-docker.jfrog.io/drone-spotinst-esg-scaler
```
