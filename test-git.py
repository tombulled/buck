import dulwich.porcelain as git
from pprint import pprint as pp
import time
import os
import os.path

"""
Currently implemented:
 Y add
 Y commit
 Y ls-files
 Y repo.get_walker (generator)
 M clean
 Y repo.get_object_by_path # git.get_object_by_path(repo, 'bar/test.txt', commit.id)

 Y describe
 M commit-tree
 M diff-tree
 Y init
 N ls-tree
 Y rm
 M reset
 M rev-list

 Y archive
 Y branch{_create,_delete,_list}
 N check-ignore
 N checkout
 M clone
 M daemon
 M fetch
 M ls-remote
 M pull
 M push
 M remote{_add}
 N receive-pack
 M tag{_create,_delete,_list}
 N upload-pack
 N update-server-info
 Y status
 M symbolic-ref

Not listed:


Notes:
    * Single branch
    * No remote repos (no pulling, pushing etc.)

Need:
    * All files should always be tracked
    * List specific file versions
"""

class Repo(object):
    def __init__(self, repo):
        self.repo = repo

    def ls(self):
        return tuple(map(bytes.decode, git.ls_files(repo)))

    def clean(self):
        git.clean(self.repo, self.repo.path)

    def status(self):
        status = git.status(self.repo)

        return status._asdict

    def get_untracked_paths(self):
        return self.status()['untracked']

    def get_unstaged_changes(self):
        return self.status()['unstaged']

    def walk_commits(self):
        return (item for item in self.repo.get_walker())

    def get_commit_changes(self, commit_id):
        for entry in self.repo.get_walker():
            if entry.commit.id == commit_id:
                return entry.changes()

# Create repo
# git.init('/tmp/some-repo')

# Get repo
repo = git.Repo('/tmp/some-repo')

r = Repo(repo)

# Create archive
git.archive(repo)
print('Archive ^^^')

# Create branch
git.branch_create(repo, 'dev')

# Delete branch
git.branch_delete(repo, 'dev')

# List branches:
branches = tuple(map(bytes.decode, git.branch_list(repo)))
print('Branches:', branches)

# Make file change
with open('/tmp/some-repo/foo.txt', 'w') as file:
    file.write(f'Hello! - {time.time()}')

# Make directory
if not os.path.isdir('/tmp/some-repo/bar'):
    os.mkdir('/tmp/some-repo/bar')

# Add file + directory
git.add(repo, '/tmp/some-repo/foo.txt')
# git.add(repo, '/tmp/some-repo/bar') # Doesn't keep track of directories

# Stage changes
# git.add(repo) - doesnt work
repo.stage([b'bar/test.txt'])

# Commit change
git.commit(repo, f'Some description here - {time.time()}')
# repo.do_commit(b'some message - yes bytes')

# Get head
print('Head:', repo.head())

# Get description
print('Description:', git.describe(repo))

# Get commit
commit = repo[repo.head()]

# List files
files = tuple(map(bytes.decode, git.ls_files(repo)))
print('Files:', files)

# List tree
git.ls_tree(repo)
print('Tree listing ^^^')

# Remove file
git.rm(repo, ['/tmp/some-repo/foo.txt'])

# Get status
status = git.status(repo)
print('Status:', status)

# Get active branch
active_branch = git.active_branch(repo).decode()
print('Active branch:', active_branch)

# Get branch remote
remote = git.get_branch_remote(repo)
print('Remote:', remote)

# Get tree changes
changes = git.get_tree_changes(repo)
print('Changes:', changes)

# Get object
obj = git.get_object_by_path(repo, 'foo.txt')
print('Object:', obj)
