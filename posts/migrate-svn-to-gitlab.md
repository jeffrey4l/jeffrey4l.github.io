Title: Migrate SVN to GitLab
Date: 2014-08-12
Tags: git
Email: zhang.lei.fly@gmail.com

* 在GitLab上创建相对应的项目/项目组
* 准备''users.txt''文件，来修正提交用户名。并手动修改users.txt的正确性 
```
svn log <svn-url> --xml | grep -P "^<author" | sort -u | perl -pe 's/<author>(.*?)<\/author>/$1 = /' > users.txt
```
users.txt的文件格式如下
```text
Lei Zhang = Lei Zhang <zhang.lei.fly#gmail.com>
```
* 把SVN项目使用git-svn进行克隆 
```
git svn clone --no-metadata --authors-file users.txt -s <svn-url> <project>
```
* 处理SVN的分支和标签 
```
cd <project>
git for-each-ref refs/remotes/tags | cut -d / -f 4- | grep -v @ | while read tagname; do git tag "$tagname" "tags/$tagname"; git branch -r -d "tags/$tagname"; done
git for-each-ref refs/remotes | cut -d / -f 3- | grep -v @ | while read branchname; do git branch "$branchname" "refs/remotes/$branchname"; git branch -r -d "$branchname"; done</code>
```
* Push到Gitlab上的仓库
```
git remote add origin <git-repo-url>
git push origin --all
git push origin --tags
```

## 参考
[Git and Other Systems - Migrating to Git](http://git-scm.com/book/en/Git-and-Other-Systems-Migrating-to-Git)
