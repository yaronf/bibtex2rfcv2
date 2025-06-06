import bibtexparser

bibtex_str = """
@InProceedings{weakkeys12,
  author = {Nadia Heninger and Zakir Durumeric and Eric Wustrow and J. Alex Halderman},
  title = {Mining Your {P}s and {Q}s: {D}etection of Widespread Weak Keys in Network Devices},
  booktitle = {Proceedings of the 21st {USENIX} Security Symposium},
  month = aug,
  year = 2012
}
"""

parser = bibtexparser.loads(bibtex_str)
print(parser.entries) 