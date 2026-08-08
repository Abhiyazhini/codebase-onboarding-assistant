import os
import shutil
import stat
from git import Repo

def remove_readonly(func, path, _):
    """Clears the read-only flag on Windows files so shutil.rmtree can delete them."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(github_url: str, dest_folder: str = "cloned_repo"):
    """Clones a repo. Deletes any old clone first so re-runs don't break."""
    if os.path.exists(dest_folder):
        # Added onexc parameter to handle Windows read-only git files
        shutil.rmtree(dest_folder, onexc=remove_readonly)
    Repo.clone_from(github_url, dest_folder, depth=30)
    return dest_folder

def get_python_files(repo_path: str):
    """Walks the repo and returns paths to all .py files, skipping junk folders."""
    skip_dirs = {".git", "venv", "__pycache__", "node_modules", ".venv"}
    py_files = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files

def get_recent_commits_for_file(repo_path: str, file_path: str, max_count: int = 5):
    """Returns last N commit messages + dates for a specific file."""
    repo = Repo(repo_path)
    relative_path = os.path.relpath(file_path, repo_path)
    commits = list(repo.iter_commits(paths=relative_path, max_count=max_count))
    history = []
    for c in commits:
        history.append({
            "message": c.message.strip(),
            "author": c.author.name,
            "date": c.committed_datetime.strftime("%Y-%m-%d"),
        })
    return history