#!/bin/bash

TAGGED_VERSION="$(git tag --points-at HEAD)"
RELEASE_URL="https://${CI_SERVER_HOST}/${CI_PROJECT_PATH}/-/releases/${TAGGED_VERSION}"

read -d '' MESSAGE << EOF
{
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "${CI_PROJECT_NAME}: <${RELEASE_URL}|${TAGGED_VERSION}> now available :tada:"
      }
    }
  ]
}
EOF

echo $MESSAGE | curl -X POST -H 'Content-type: application/json' --data-binary @- $SLACK_WEBHOOK_URL
