#!/usr/bin/env python
import argparse
import json
import subprocess

from datetime import datetime, timedelta

DEFAULT_OWNER = 'areaDetector'
DEFAULT_SKIP_REPOS = [
    'ADKinetix', # has disabled issues
]
DEFAULT_FIRST_REPOS = [
    'areaDetector',
    'ADCore',
    'ADSupport',
]
DEFAULT_MAX_DAYS_OLD = 31


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--owner', default=DEFAULT_OWNER)
    parser.add_argument('--repos', nargs='+', default=None)
    parser.add_argument('--skip-repos', nargs='+', default=DEFAULT_SKIP_REPOS)
    parser.add_argument('--first-repos', nargs='+', default=DEFAULT_FIRST_REPOS)
    parser.add_argument('--no-skip-archived', action='store_false', dest='skip_archived')
    parser.add_argument('--days', type=int, default=DEFAULT_MAX_DAYS_OLD)
    return parser.parse_args()


def parse_time(time_str):
    return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')


def filter_old(items, days):
    now = datetime.now()
    return [item for item in items
            if now - parse_time(item['updatedAt']) <= timedelta(days=days)]


def get_repos(owner, skip_archived):
    command = ['gh', 'repo', 'list', '--limit', '1000', '--json', 'name']
    if skip_archived:
        command += ['--no-archived']
    command += [owner]
    output = subprocess.check_output(command)
    repos = json.loads(output)
    return [repo['name'] for repo in repos]


def sort_repos(repos, first_repos):
    repos_set = set(repos)
    first_repos_set = set(first_repos)

    # sort repositories after first_repos
    repos = list(repos_set - first_repos_set)
    repos.sort()

    # only include first_repos that were in the main list
    first_repos = [repo for repo in first_repos if repo in repos_set]

    return first_repos + repos


def get_issues(project):
    output = subprocess.check_output(['gh', 'issue', 'list', '--json',
                                      'title,url,updatedAt', '--repo',
                                      project])
    return json.loads(output)


def get_prs(project):
    output = subprocess.check_output(['gh', 'pr', 'list', '--json',
                                      'title,url,updatedAt', '--repo',
                                      project])
    return json.loads(output)


def main():
    args = parse_args()
    if args.repos is None:
        repos = get_repos(args.owner, skip_archived=args.skip_archived)
    else:
        repos = args.repos

    repos = sort_repos(repos, args.first_repos)

    for repo in repos:
        if repo in args.skip_repos:
            continue
        project = f'{args.owner}/{repo}'
        issues = get_issues(project)
        issues = filter_old(issues, args.days)
        prs = get_prs(project)
        prs = filter_old(prs, args.days)
        if not issues and not prs:
            continue

        print(f'- {repo}:')
        if issues:
            print('    - Issues:')
            for issue in issues:
                print('        - [ ] [%s](%s)' % (issue['title'],
                                                  issue['url']))

        if prs:
            print('    - PRs:')
            for pr in prs:
                print('        - [ ] [%s](%s)' % (pr['title'], pr['url']))


if __name__ == '__main__':
    main()
