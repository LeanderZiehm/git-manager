import os
import subprocess


def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))


def has_unpushed_commits(path):
    try:
        # Fetch latest remote info
        subprocess.run(
            ["git", "fetch"],
            cwd=path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Check if HEAD is attached
        branch = (
            subprocess.check_output(
                ["git", "symbolic-ref", "--short", "HEAD"],
                cwd=path,
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )

        # Check if branch has an upstream
        subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            cwd=path,
            stderr=subprocess.DEVNULL,
        )

        # Compare local and remote commits
        local = subprocess.check_output(["git", "rev-parse", "@"], cwd=path).strip()
        remote = subprocess.check_output(["git", "rev-parse", "@{u}"], cwd=path).strip()
        base = subprocess.check_output(
            ["git", "merge-base", "@", "@{u}"], cwd=path
        ).strip()

        if local == remote:
            return False  # Up to date
        elif remote == base:
            return True  # Ahead
        else:
            return True  # Diverged (ahead and behind)

    except subprocess.CalledProcessError:
        # Detached HEAD, no upstream, or other error — skip
        return False


def main():
    for entry in os.listdir("."):
        path = os.path.join(".", entry)
        if os.path.isdir(path) and is_git_repo(path):
            if has_unpushed_commits(path):
                print(f"{entry} has unpushed commits.")
            else:
                print(f"{entry} is up to date.")
                # delete the repo
                subprocess.run(["rm", "-rf", path], check=True)


if __name__ == "__main__":
    main()
