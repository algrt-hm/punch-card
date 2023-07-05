#!/bin/bash

./punch-card.sh -s && \
nice -n 20 ./punch-card.sh -a && \
./punch-card.sh -s
