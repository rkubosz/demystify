# This file is part of Demystify.
# 
# Demystify: a Magic: The Gathering parser
# Copyright (C) 2012 Benjamin S Wolf
# 
# Demystify is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
# 
# Demystify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

"""test -- An automatic unittest interpreter for Demystify."""

import argparse
import difflib
import os
import re
import unittest

import antlr4

from grammar import DemystifyLexer, DemystifyParser

_rule_name = re.compile(r'\w+')

class IgnoreCaseDiffer(difflib.Differ, object):
    """ Compares two string sequences but ignores case. """
    def compare(self, a, b):
        if isinstance(a, str):
            a = [a]
        else:
            a = list(a)
        if isinstance(b, str):
            b = [b]
        else:
            b = list(b)
        diff = super(IgnoreCaseDiffer, self).compare(
                [s.lower() for s in a], [t.lower() for t in b])
        i = 0
        j = 0
        c = []
        for l in diff:
            if l.startswith('- '):
                c.append('- ' + a[i])
                i += 1
            elif l.startswith('+ '):
                c.append('+ ' + b[j])
                j += 1
            elif l.startswith('  '):
                c.append('  ' + a[i])
                i += 1
                j += 1
            else:
                c.append(l)
        return c

def _token_stream(name, text):
    """ Helper method for generating a token stream from text. """
    char_stream = antlr4.ANTLRStringStream(text)
    lexer = DemystifyLexer.DemystifyLexer(char_stream)
    lexer.card = name
    # tokenizes completely and logs on errors
    return antlr4.CommonTokenStream(lexer)

def parse_text(name, rule, text):
    ts = _token_stream(name, text)
    p = DemystifyParser.DemystifyParser(ts)
    p.setCardState(name)
    result = getattr(p, rule)()
    return result

def generate_tests(filename):
    errors = 0
    with open(filename) as f:
        name = None
        rule = None
        text = None
        expected = None
        lbuffer = []
        skip = False
        for i, line in enumerate(f):
            # lbuffer includes the newlines
            lbuffer.append(line.rstrip('\n'))
            if len(lbuffer) > 3:
                del lbuffer[0]
            line = line.strip()
            if skip:
                if not line:
                    skip = False
                    rule = text = expected = None
                    lbuffer = []
                continue
            if line.startswith('#'):
                continue
            if not line:
                if rule:
                    if text:
                        if expected:
                            yield (name, rule, text, expected)
                        else:
                            print('Line {}: Missing expected tree '
                                  'representation.'.format(i + 1))
                            print('\n'.join(lbuffer))
                            print('^')
                            errors += 1
                    else:
                        print("Line {}: Missing text for '{}' test."
                              .format(i + 1, rule))
                        print('\n'.join(lbuffer))
                        print('^')
                        errors += 1
                # In any case here, reset everything
                name = rule = text = expected = None
                lbuffer = []
            elif line.startswith('@'):
                line = line[1:]
                if not line:
                    print('Line {}: Must be nonempty.'.format(i + 1))
                    print('\n'.join(lbuffer))
                    print(' ^')
                    errors += 1
                    skip = True
                if rule:
                    if text:
                        if expected:
                            print('Line {}: Need one or more lines of white'
                                  'space between test cases.'.format(i + 1))
                            print('\n'.join(lbuffer))
                            print('^')
                            errors += 1
                            skip = True
                        else:
                            expected = line
                    else:
                        text = line
                else:
                    m = _rule_name.match(line)
                    l = m and m.end() or 0
                    if len(line) != l:
                        print('Line {}: Rule or test name must contain only '
                              'alphanumeric characters.'.format(i + 1))
                        print('\n'.join(lbuffer))
                        print('{caret:>{char}}'.format(caret='^', char=l))
                        errors += 1
                        skip = True
                    else:
                        if line[0].isupper():
                            name = line
                        else:
                            rule = line
                            if not name:
                                name = line.title().replace('_', '')
            else:
                # line is a continuation of the previous line
                if rule or name:
                    if text:
                        if expected:
                            expected += ' ' + line
                        else:
                            text += ' ' + line
                    else:
                        print('Line {}: Rule or test name is restricted to '
                              'one line.'.format(i + 1))
                        print('\n'.join(lbuffer))
                        print('^')
                        errors += 1
                        skip = True
                else:
                    print("Line {}: Rule or test name must be preceded by '@'."
                          .format(i + 1))
                    print('\n'.join(lbuffer))
                    print('^')
                    errors += 1
                    skip = True
        # EOF
        if rule:
            if text and expected:
                yield (name, rule, text, expected)
            else:
                print('EOF reached in middle of test case:')
                print('\n'.join(lbuffer))
                print('^')
                errors += 1
    if errors:
        print('{} errors encountered in {}.'.format(errors, filename))

def create_test_function(name, rule, text, expected):
    def test_function(self):
        result = parse_text(name, rule, text)
        d = IgnoreCaseDiffer()
        diff = d.compare([expected + '\n'], result.tree.toStringTree() + '\n')
        differror = 'Lines differ:\n--- expected\n+++ result\n'
        self.assertEqual(1, len(diff), differror + ''.join(diff))
    return test_function

def create_test_case(filename):
    fname = os.path.splitext(os.path.basename(filename))[0]
    canon_name = fname.replace('.', '_').capitalize()
    class TestCase(unittest.TestCase):
        pass
    TestCase.canon_name = canon_name
    TestCase.__name__ = canon_name + 'TestCase'
    d = {}
    for name, rule, text, exp in generate_tests(filename):
        if name not in d:
            d[name] = 1
        else:
            d[name] += 1
        name = 'test_{}{}{}'.format(canon_name, name, d[name])
        setattr(TestCase, name, create_test_function(name, rule, text, exp))
    if not d:
        print('No test cases generated for {}.'.format(filename))
        return None
    return TestCase

def add_subcommands(subparsers):
    """ Adds the 'test' command to the main parser.
        subparsers should be the object returned by add_subparsers()
        called on the main parser. """
    subparser = subparsers.add_parser('test',
        description='Run Demystify unittests.')
    subparser.add_argument('-v', '--verbosity', type=int, default=1,
        help='Verbosity level for running unittests.')
    subparser.add_argument('--test_dir',
        default=os.path.join(os.path.dirname(__file__), 'tests'),
        help='Folder containing test cases.')
    subparser.add_argument('tests', nargs='*',
        help=('List of test files to run. If omitted, all .txt files '
              'in --test_dir will be run.'))
    subparser.set_defaults(func=run_tests)

def run_tests(args):
    """ Main entry point for the 'test' subcommand.
        args is a Namespace object with the appropriate flags. """
    if args.tests:
        tests = []
        for t in args.tests:
            if os.path.exists(t):
                tests.append(t)
            else:
                print('Error: File does not exist: {}'.format(t))
    else:
        if os.path.exists(args.test_dir):
            if os.path.isdir(args.test_dir):
                tests = [os.path.join(args.test_dir, t)
                         for t in os.listdir(args.test_dir)
                         if os.path.splitext(t)[1] == '.txt']
            else:
                print('Error: Given path {} is not a directory.'
                      .format(args.test_dir))
                return
        else:
            print('Error: path {} does not exist'.format(args.test_dir))
            return
    if not tests:
        print('No test files found, exiting.')
        return
    test_cases = [create_test_case(filename) for filename in tests]
    if not any(test_cases):
        print('Error: No test cases generated.')
        return
    for tc in test_cases:
        if tc:
            suite = unittest.TestLoader().loadTestsFromTestCase(tc)
            print('Test suite: {}'.format(tc.canon_name))
            unittest.TextTestRunner(verbosity=args.verbosity).run(suite)
