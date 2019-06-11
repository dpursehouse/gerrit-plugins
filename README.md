# Dummy project to collect Gerrit plugins

This project contains several submodules, each of which is a Gerrit plugin.

## Update bazlets revision

To update the bazlets revision on all plugins:

```
git submodule foreach  ../update-bazlets.py -r 1d381f01c853e2c02ae35430a8e294e485635d62 -b stable-3.0 -v 3.0.0
git submodule foreach 'git push origin HEAD:refs/for/stable-3.0 || echo not pushed'
```

## Format code

```
git submodule foreach 'git ls-files | grep java$ | xargs google-java-format -i'
git submodule foreach 'git commit -a -m "Format all Java files with google-java-format" || echo nothing to commit'
git submodule foreach 'git push origin HEAD:refs/for/stable-3.0 || echo not pushed'
```

## Format build files

```
git submodule foreach 'git ls-files | grep "WORKSPACE\|BUILD\|\.bzl$" | xargs buildifier -mode=fix'
git submodule foreach 'git commit -a -m "Format all Bazel build files with buildifier" || echo nothing to commit'
git submodule foreach 'git push origin HEAD:refs/for/stable-3.0 || echo not pushed'
```

## Update submodules

```
git submodule foreach 'git fetch && git checkout -q origin/stable-3.0'
git commit -a -m "Update revisions"
git push origin HEAD:stable-3.0
```

## Merge-up to here

```
git submodule foreach 'git checkout stable-2.16 && git pull'
git submodule foreach 'git checkout stable-3.0 && git pull'
git submodule foreach 'git merge stable-2.16 --no-commit --no-ff || echo no merge'
git submodule foreach 'vi WORKSPACE'
git submodule foreach 'git diff || echo no diff'
git submodule foreach 'f=`git rev-parse --git-dir`/hooks/commit-msg; curl -Lo $f https://gerrit-review.googlesource.com/tools/hooks/commit-msg; chmod +x $f'
git submodule foreach 'git commit -a || echo nothing to commit'
git submodule foreach 'git status'
git submodule foreach 'git push origin HEAD:refs/for/stable-3.0 || echo not pushed'
git submodule foreach 'git reset origin/stable-3.0'
```

## Review merge-up change using bazel
### PoC, CI otherwise; assumes jq

```
git submodule foreach 'curl -s -o change.json https://gerrit-review.googlesource.com/changes/?q=project:plugins/$name+status:open+branch:stable-3.0+merge+branch\&n=1\&o=CURRENT_REVISION\&o=DOWNLOAD_COMMANDS || echo no change'
git submodule foreach 'tail --lines=+2 change.json | jq -r ".[0].revisions[].fetch.http.commands.Checkout" > change.fetch || echo no command'
git submodule foreach 'chmod +x change.fetch && ./change.fetch || echo no fetch'
git submodule foreach 'git log -n 1'
git submodule foreach 'bazel clean --expunge && bazel build $name || echo no standalone'
git submodule foreach 'bazel test //... || echo no tests'
git submodule foreach 'rm change.json change.fetch || echo no files'
git submodule foreach 'git checkout -q origin/stable-3.0'
```

## Review bazlets upgrade change
### -works with trailing commands above

```
git submodule foreach 'curl -s -o change.json https://gerrit-review.googlesource.com/changes/?q=project:plugins/$name+status:open+branch:stable-3.0+Upgrade+bazlets\&n=1\&o=CURRENT_REVISION\&o=DOWNLOAD_COMMANDS || echo no change'
```

