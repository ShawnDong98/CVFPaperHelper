import requests
import os
import re
from typing import List
from tqdm import tqdm


CVF_URL = "https://openaccess.thecvf.com/"


def download_file(url, dir, filename):
    print(url)
    print(filename)
    r = requests.get(url, allow_redirects=True)
    open(f"{dir}/{filename.replace(':', '：').replace('?', '？')}.pdf", 'wb').write(r.content)


def mkdir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


class CVPRHelper:
    def __init__(self, year) -> None:
        self.year = str(year)
        webpage = requests.get(
            f"https://openaccess.thecvf.com/CVPR{year}?day=all").text
        open('temp.html', 'w').write(webpage)
        webpage = open('temp.html').read()
        # pattern = r"<dd>\n\[.*?</div>"
        pattern = r"<dd>\n\n\[.*?</div>"
        pattern = re.compile(pattern, re.DOTALL)
        # print(f"pattern: {pattern}")
        paper_list = re.findall(pattern, webpage)
        # print(f"paper_list: {paper_list}")

        paper_list_in_lines = [raw.split('\n') for raw in paper_list]

        bibex_pattern = re.compile(
            "<div class=\"bibref pre-white-space\">.*?</div>", re.DOTALL)
        
        bibex_list_in_lines = [re.findall(bibex_pattern, raw)[
            0].split('\n') for raw in paper_list]

        # print(f"bibex_list_in_lines: {bibex_list_in_lines}")
        # test = [lines for lines in paper_list_in_lines]


        self.urls = [CVF_URL+lines[2][10:-10] for lines in paper_list_in_lines]
        self.authors = [lines[1].strip()[13:-2]
                        for lines in bibex_list_in_lines]
        self.titles = [lines[-6].strip()[13:-2]
                       for lines in bibex_list_in_lines]

    def search_keyword(self, kw) -> List[int]:
        result = []
        for idx, title in enumerate(self.titles):
            if kw.lower() in title.lower():
                result.append(idx)
        print(f"found {len(result)} papers")
        return result

    def download_paper(self, idx, save_to):
        download_file(self.urls[idx], save_to, filename=self.titles[idx])

    def download_keyword(self, kw):
        download_dir = f"./CVPR{self.year}-{kw}/"
        mkdir(download_dir)
        paper_idx_list = self.search_keyword(kw)
        bar = tqdm(paper_idx_list)
        for paper_idx in bar:
            self.download_paper(paper_idx, download_dir)
            bar.set_description(
                f"Downloading \"{self.titles[paper_idx][:10]}...\"")
