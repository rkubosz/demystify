import os
import re
import sys

rule = re.compile(r"^(?:[a-z_0-9]+\+?=)?([a-z_0-9]+)\+?\*?!?\??$")
comments = re.compile(r"//.*$|/\*.*\*/", re.M)
actions = re.compile(r"""{([^'"]|'[^']*'|"[^"]*"|'''.*?'''"""
                     r'''|""".*?""")*}''', re.M)
full_rule = re.compile(r"^([a-z_0-9]+)\s*:(.*);\s*$", re.M)

def find_rules(fulltext):
    """ fulltext is the full text of the file. """
    ct = comments.sub(' ', fulltext)
    nt = ct.replace('\n ', ' ')
    deps = {}
    for m in full_rule.finditer(nt):
        rname, rtext = m.groups()
        rt = actions.sub('', rtext)
        deps[rname] = set()
        for token in rt.split():
            m = rule.match(token)
            if m:
                deps[rname].add(m.group(1))
    return deps

def print_deps(deps):
    for rname, rdeps in deps.items():
        for d in rdeps:
            print('  "{}" -> "{}";'.format(rname, d))

basedir = os.path.join(os.path.dirname(__file__), 'grammar')

def print_graph(files):
    print('digraph gdeps {\n  truecolor=true;')
    # filename -> list of deps
    fdeps = {}
    # rule name -> filename
    dep_file = {}
    # filename -> filename it depends on
    file_deps = {}
    for f in files:
        with open(os.path.join(basedir, f)) as g:
            s = g.read()
        f = os.path.basename(f)
        deps = find_rules(s)
        fdeps[f] = deps
        for rname in deps:
            dep_file[rname] = f
        file_deps[f] = set()
    for f, deps in fdeps.items():
        color = colors[f]
        g = os.path.splitext(f)[0]
        print('  subgraph "{g}" {{\n    node [style=filled,color={c}];\n'
              .format(g=g, c=color))
        for rname, rdeps in deps.items():
            print('    {};'.format(rname))
            for rdep in rdeps:
                if dep_file[rname] != dep_file[rdep]:
                    file_deps[dep_file[rname]].add(dep_file[rdep])
        print('  }')
    for deps in fdeps.values():
        print_deps(deps)
    print('  subgraph "files" {')
    for fname, fdeps in file_deps.items():
        print('    "{}" [shape=box,style=filled,color={}];'
              .format(fname, colors[fname]))
    print_deps(file_deps)
    print('  }\n}')

colors = {
    'misc.g': 'red',
    'players.g': 'blue',
    'zones.g': 'green',
    'macro.g': 'cyan',
    'types.g': 'lightgray',
    'costs.g': 'gold',
    'Demystify.g': 'plum',
    'pt.g': 'seagreen',
    'subsets.g': 'greenyellow',
    'math.g': 'violetred',
}

if __name__ == "__main__":
    print_graph(colors.keys())
