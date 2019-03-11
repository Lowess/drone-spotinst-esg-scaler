#!/usr/bin/env python

"""Adjust the capacity of a Spotinst ESG."""

import sys
import requests

from requests.exceptions import RequestException

from plugin import logger, dronecli


class SpotinstEsgScaler():
    """ECSAutoscaler object managing service registration as a scalable target."""

    def __init__(self, api_token, account_id, esg_name, adjustment_type, adjustment):
        """Create an ECSAutoscaler."""
        self._api_root = "https://api.spotinst.io"
        self._account_id = account_id
        self._api_token = api_token
        self._esg_name = esg_name
        self._adjustment_type = adjustment_type
        self._adjustment = int(adjustment)

        # Fill in the ESG ID based on the name
        esg_id_req = self.request(
            url=self._preprocess(endpoint="/aws/ec2/group", options=dict(name=self._esg_name)))

        logger.debug(esg_id_req)
        self._esg_id = esg_id_req['items'][0]['id']
        self._esg_capacity = esg_id_req['items'][0]['capacity']

    def __repr__(self):
        """Representation of an ECSAutoscaler object."""
        return "<{} 'api_token': {}, 'esg_name': {}, 'esg_id': {}, 'esg_capacity': {}".format(
            self.__class__,
            self._api_token[:3] + "x" * len(self._api_token[3:]),
            self._esg_name,
            self._esg_id,
            self._esg_capacity
        )

    def request(self, url, method='get'):
        """Make request to spotinst."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self._api_token)
        }

        try:
            r = None
            if method == 'get':
                r = requests.get(url=url, headers=headers)
            elif method == 'post':
                r = requests.post(url=url, headers=headers)
            elif method == 'put':
                r = requests.put(url=url, headers=headers)
            else:
                logger.error("{} is not supported by this fuction.")
                sys.exit(1)

            r_json = r.json()
            r.raise_for_status()

            return r_json['response']

        except RequestException as e:
            e_msg = "(-)"
            try:
                e_msg = r_json['response']['errors'][0]['message']
            except Exception:
                pass
            logger.error("Error occured while making the following request: {} {} - Error details: {}".format(url, e, e_msg))
            sys.exit(1)

    def _preprocess(self, endpoint, options):
        """Prepare a query with common arguments."""
        query = self._api_root
        query += endpoint
        query += "?accountId={}".format(self._account_id)
        query += ''.join({"&{}={}".format(k, v) for (k, v) in options.items()})

        logger.info("Query path built: {}".format(query))
        return query

    def _compute_size(self):
        """Compute the new size of the ESG based on the adjustment type and adjustment chosen."""
        if self._adjustment_type == 'count':
            logger.info("Adding instances to the ESG {} ({}) from {} -> {}".format(
                self._esg_name,
                self._esg_id,
                self._esg_capacity['target'],
                self._esg_capacity['target'] + self._adjustment))

        elif self._adjustment_type == 'double':
            self._adjustment = self._esg_capacity['target'] * 2
            logger.info("Doubling the size of the ESG {} ({}) from {} -> {}".format(
                self._esg_name,
                self._esg_id,
                self._esg_capacity['target'],
                self._adjustment))

        elif self._adjustment_type == 'half':
            self._adjustment = int(round(self._esg_capacity['target'] / 2)) + self._esg_capacity['target']
            logger.info("Adding half the size of the ESG {} ({}) from {} -> {}".format(
                self._esg_name,
                self._esg_id,
                self._esg_capacity['target'],
                self._adjustment))
        else:
            raise Exception("Adjustment type unkown, please use one of ['count', 'double', 'half']")

    def setup(self):
        """Main plugin logic."""
        self._compute_size()

        esg_adjust_req = self.request(
            method='put',
            url=self._preprocess(endpoint="/aws/ec2/group/{}/scale/up".format(self._esg_id),
                                 options=dict(adjustment=self._adjustment))
        )

        logger.info("Scale up request successful! {}".format(esg_adjust_req['items'][0]))


def main():
    """The main entrypoint for the plugin."""
    try:
        api_token = dronecli.get('API_TOKEN')

        account_id = dronecli.get('PLUGIN_ACCOUNT_ID')
        esg_name = dronecli.get('PLUGIN_ESG_NAME')
        adjustment_type = dronecli.get('PLUGIN_ADJUSTMENT_TYPE', default='count')
        adjustment = dronecli.get('PLUGIN_ADJUSTMENT', default=1)

        plugin = SpotinstEsgScaler(
            api_token=api_token,
            account_id=account_id,
            esg_name=esg_name,
            adjustment_type=adjustment_type,
            adjustment=adjustment
        )

        logger.info("The drone plugin has been initialized with: {}".format(plugin))

        plugin.setup()

    except Exception as e:
        logger.error("Error while executing the plugin: {}".format(e))
        raise e
        sys.exit(1)


if __name__ == "__main__":
    main()
