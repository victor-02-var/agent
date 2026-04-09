import pydriller
from radon.complexity import cc_visit

class GitForensics:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def analyze_hotspots(self):
        # Scans history for high-churn files
        hotspots = {}
        for commit in pydriller.Repository(self.repo_path).traverse_commits():
            for m in commit.modified_files:
                hotspots[m.filename] = hotspots.get(m.filename, 0) + 1
        return hotspots

    def get_complexity(self, code_string):
        # Returns cyclomatic complexity
        try:
            results = cc_visit(code_string)
            return sum([res.complexity for res in results])
        except:
            return 0