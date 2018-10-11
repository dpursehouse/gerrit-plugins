# Dummy project to collect Gerrit plugins

This project contains several submodules, each of which is a Gerrit plugin.

## Update bazlets revision

To update the bazlets revision on all plugins:

```
git submodule foreach  ../update-bazlets.py -r 0cdf281f110834b71ae134afe0a7e3fe346f0078 -b stable-2.14 -v 2.14.15
```

To push all plugins:

```
git submodule foreach 'git push origin HEAD:refs/for/stable-2.14 || echo not pushed'
```
