from pathlib import Path


class MarkdownParser():

    def __init__(self, text):
        self.text = text
        self.lines = text.split('\n')

    def title(self):
        return self.lines[0].split(' ')[1]

    def header(self, name, level, include_header=False):
        start = False
        end = False
        content = []
        mark = '#' * level
        for line in self.lines:
            if start and not end:
                end |= (f'{mark} ' in line[:(level + 1)]) and (not f'{mark} {name}' in line)
                if end:
                    start = False
                else:
                    content.append(line)
            else:
                start = (f'{mark} {name}' in line)
                if start:
                    end = False
                    if include_header:
                        content.append(line)

        content = '\n'.join(content)
        return content

    def overview(self):
        overview = self.header('Overview', 2)
        overview = overview.split('\n')
        overview = '\n'.join(overview[1:])  # remove the first line
        return overview

    def features(self):
        return self.header('C++', 2, True)


def combine(text, parsers):
    overview = ''
    features = ''
    title = ''
    for p in parsers:
        title += p.title().replace('C++', '') + '/'
        overview += p.overview() + '\n'
        features += p.features() + '\n'

    title = title[:-1]
    overview = overview.replace('README.md#', '#')
    features = features.replace('README.md#', '#')

    text = text.replace('# C++\n', f'# C++{title}\n')
    text = text.replace(f'<!-- overview -->', overview)
    text = text.replace(f'<!-- features -->', features)

    return text


def main():
    src_dir = Path(__file__).parent
    parsers = []

    srcs = list(src_dir.glob('CPP*.md'))
    srcs.sort(reverse=True)
    for file in srcs:
        with open(file, 'r') as fp:
            text = fp.read()
        p = MarkdownParser(text)
        parsers.append(p)

    template_file = src_dir / 'readme-template.md'
    with open(template_file, 'r') as fp:
        text = fp.read()

    text = combine(text, parsers)

    readme_file = src_dir / 'README.md'
    with open(readme_file, 'w') as fp:
        fp.write(text)


if __name__ == '__main__':
    main()
