#!/usr/bin/env python
import argparse
import json
import subprocess

from datetime import datetime, timedelta

DEFAULT_OWNER = 'areaDetector'
DEFAULT_REPOS = [
    'areaDetector', 'ADCore', 'ADEiger', 'ADAravis', 'ADGenICam',
    'ADSpinnaker', 'ADVimba', 'ADAndor3', 'ADAndor', 'ADSimDetector',
    'specsAnalyser', 'ADPylon', 'pvaDriver', 'ADPvCam', 'ADSupport', 'ADUVC',
    'ADBitFlow', 'ADLambda', 'ADProsilica', 'ADPluginBar', 'ffmpegServer',
    'ADCompVision', 'ADViewers', 'ADQImaging', 'ADPICam', 'ADCSimDetector',
    'NDDriverStdArrays', 'ADSBIG', 'ADPSL', 'ADSBIG', 'ADPerkinElmer',
    'ADLightField', 'ADFireWireWin', 'ADDexela', 'ADPilatus', 'ADMythen',
    'ADmar345', 'ADRIXSCam', 'ADURL', 'ADmarCCD', 'ADPointGrey', 'ADFastCCD',
    'ADPixirad', 'ADPcoWin', 'ADPhotron', 'ADPluginCentroids', 'ADADSC',
    'ADBruker', 'ADPhotonII', 'ADRoper', 'ADnED', 'ADPluginEdge', 'ADPCO',
    'ADMerlin', 'ADMMPAD', 'ADCameralink', 'ADTimePix', 'firewireDCAM',
    'ADBinaries', 'ffmpegViewer', 'ADExample'
]
DEFAULT_MAX_DAYS_OLD = 31


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--owner', default=DEFAULT_OWNER)
    parser.add_argument('--repos', nargs='+', default=DEFAULT_REPOS)
    parser.add_argument('--days', type=int, default=DEFAULT_MAX_DAYS_OLD)
    return parser.parse_args()


def parse_time(time_str):
    return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')


def filter_old(items, days):
    now = datetime.now()
    return [item for item in items
            if now - parse_time(item['updatedAt']) <= timedelta(days=days)]


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
    for repo in args.repos:
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
