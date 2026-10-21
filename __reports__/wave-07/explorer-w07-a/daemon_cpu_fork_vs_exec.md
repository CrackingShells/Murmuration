== only=1 (1=fork-only, 0=exec spawn)
| daemon | spawn window cpu s (per pair) | idle window cpu s (per pair) | (spawn - idle) ms per spawn, median [min, max] over pairs |
|:--|:--|:--|:--|
| com.crowdstrike.falcon.Agent | 0.51 0.35 0.22 0.39 | 0.63 0.99 0.45 0.40 | -0.17 [-0.23, 0.02] |
| opendirectoryd | 0.34 0.57 0.29 0.12 | 0.43 0.84 0.28 0.06 | 0.04 [-0.09, 0.08] |
| logd | 0.01 0.01 0.01 0.00 | 0.01 0.02 0.00 0.01 | -0.00 [-0.01, 0.01] |
| syspolicyd | 0.03 0.00 0.00 0.00 | 0.00 0.00 0.00 0.01 | 0.00 [-0.01, 0.03] |
== only=0 (1=fork-only, 0=exec spawn)
| daemon | spawn window cpu s (per pair) | idle window cpu s (per pair) | (spawn - idle) ms per spawn, median [min, max] over pairs |
|:--|:--|:--|:--|
| opendirectoryd | 16.58 70.05 26.43 31.00 | 12.06 14.23 20.77 10.23 | 12.25 [4.53, 24.96] |
| com.crowdstrike.falcon.Agent | 15.65 50.80 16.63 37.51 | 18.18 26.96 19.67 10.84 | -2.78 [-34.63, 24.62] |
| fseventsd | 0.07 0.91 0.11 6.59 | 2.93 12.71 1.94 0.94 | -2.34 [-39.37, 5.47] |
| mds | 0.02 4.21 0.04 0.57 | 0.31 3.71 0.46 0.14 | -0.35 [-7.55, 0.40] |
