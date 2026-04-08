import os
import subprocess
import random
from datetime import datetime, timedelta
from pathlib import Path

def get_all_files(directory):
    files_list = []
    for root, _, files in os.walk(directory):
        if '.git' in root:
            continue
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list

def main():
    # Configuration
    days_back = 30
    commits_per_day = 2

    # Initialize git if not already
    if not os.path.exists('.git'):
        subprocess.run(['git', 'init'], check=True)

    all_files = get_all_files('.')
    if not all_files:
        print("No files found to commit.")
        return

    # Shuffle files to commit them in random order
    random.shuffle(all_files)

    # Calculate how many files to commit per step
    total_commits = days_back * commits_per_day
    chunk_size = max(1, len(all_files) // total_commits)

    start_date = datetime.now() - timedelta(days=days_back)

    file_index = 0
    current_date = start_date

    print(f"Starting to backdate {len(all_files)} files over {days_back} days...")

    for i in range(total_commits):
        if file_index >= len(all_files):
            break

        # Get chunk of files for this commit
        chunk = all_files[file_index:file_index + chunk_size]
        file_index += chunk_size

        # Add files to git
        for f in chunk:
            subprocess.run(['git', 'add', f])

        # Generate commit message based on added files
        file_names = [os.path.basename(f) for f in chunk]
        commit_msg = f"Add {', '.join(file_names[:2])}" + (" and other files" if len(file_names) > 2 else "")

        # Format date for git
        # Advance time a bit for each commit
        current_date += timedelta(hours=random.randint(2, 8))
        date_str = current_date.strftime('%Y-%m-%dT%H:%M:%S')

        # Set environment variables for committer date
        env = os.environ.copy()
        env['GIT_AUTHOR_DATE'] = date_str
        env['GIT_COMMITTER_DATE'] = date_str

        # Commit
        subprocess.run(['git', 'commit', '-m', commit_msg], env=env)
        print(f"Committed {len(chunk)} files on {date_str}")

    # Commit any remaining files
    if file_index < len(all_files):
        remaining = all_files[file_index:]
        for f in remaining:
            subprocess.run(['git', 'add', f])

        current_date += timedelta(hours=1)
        date_str = current_date.strftime('%Y-%m-%dT%H:%M:%S')
        env = os.environ.copy()
        env['GIT_AUTHOR_DATE'] = date_str
        env['GIT_COMMITTER_DATE'] = date_str

        subprocess.run(['git', 'commit', '-m', "Finalize remaining project files"], env=env)
        print(f"Committed final {len(remaining)} files on {date_str}")

    print("\nDone! You can now run 'git push origin main' to upload to GitHub.")
    print("Disclaimer: This modifies local git history. Verify with 'git log' before pushing.")

if __name__ == '__main__':
    main()
