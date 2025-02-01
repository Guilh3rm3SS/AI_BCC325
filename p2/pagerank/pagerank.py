import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    dictionary = {}
    num_pages = len(corpus)
    num_links = len(corpus[page])
    
    if num_links == 0:
        for c_page in corpus:
            dictionary[c_page] = 1 / num_pages

    else: 
        for c_page in corpus:
            dictionary[c_page] = (1 - damping_factor) * 1 / num_pages
        for link_page in corpus[page]:
            dictionary[link_page] += damping_factor * 1 / num_links
    
    return dictionary
    
    
def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    sample = {page: 0 for page in corpus}
    dictionary = {}
    page = random.choice(list(corpus.keys()))
    
    for i in range(n):
        sample[page] += 1/n
        dictionary = transition_model(corpus, page, damping_factor)
        page = random.choices(list(dictionary.keys()), weights=dictionary.values(), k=1)[0]
    
    return sample
            
            
def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    dictionary = {}
    convergence = False

    for page in corpus:
        dictionary[page] = 1 / len(corpus)
    
    while convergence == False:
        new_dictionary = {}
        for page in corpus:
            new_dictionary[page] = (1-damping_factor) / len(corpus)
            for i_page in corpus:
                if len(corpus[i_page]) != 0:
                    if page in corpus[i_page]:
                        new_dictionary[page] += damping_factor * dictionary[i_page] / len(corpus[i_page])
                else:
                    new_dictionary[page] += damping_factor * dictionary[i_page] / len(corpus)
            
        convergence = all(abs(dictionary[page] - new_dictionary[page]) < 0.001  for page in corpus)
        dictionary = new_dictionary.copy()
        
    return dictionary

if __name__ == "__main__":
    main()
