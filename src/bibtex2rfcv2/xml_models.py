"""RFC XML v3 reference models for BibTeX to RFC conversion."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from xml.sax.saxutils import escape
from bibtex2rfcv2.utils import latex_to_unicode


@dataclass
class Author:
    """RFC XML author information."""

    fullname: str
    initials: Optional[str] = None
    surname: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    uri: Optional[str] = None
    ascii_fullname: Optional[str] = None
    ascii_initials: Optional[str] = None
    ascii_surname: Optional[str] = None
    ascii_organization: Optional[str] = None

    def __init__(self, fullname: str, initials: Optional[str] = None, surname: Optional[str] = None,
                 organization: Optional[str] = None, role: Optional[str] = None, email: Optional[str] = None,
                 uri: Optional[str] = None, ascii_fullname: Optional[str] = None, ascii_initials: Optional[str] = None,
                 ascii_surname: Optional[str] = None):
        self.fullname = fullname
        self.initials = initials
        self.surname = surname
        self.organization = organization
        self.role = role
        self.email = email
        self.uri = uri
        self._ascii_fullname = ascii_fullname
        self._ascii_initials = ascii_initials
        self._ascii_surname = ascii_surname

    def to_xml(self) -> str:
        """Convert author to XML."""
        # Convert LaTeX accents to Unicode and clean up the name
        unicode_name = latex_to_unicode(self.fullname)
        clean_name = unicode_name.strip().replace("\n", " ").replace("{", "").replace("}", "").replace("\\", "")
        # Build attributes for this author
        attrs = [f'fullname="{escape(clean_name)}"']
        if self.initials:
            attrs.append(f'initials="{escape(self.initials)}"')
        if self.surname:
            attrs.append(f'surname="{escape(self.surname)}"')
        if self.organization:
            attrs.append(f'organization="{escape(self.organization)}"')
        if self.role:
            attrs.append(f'role="{escape(self.role)}"')
        if self.email:
            attrs.append(f'email="{escape(self.email)}"')
        if self.uri:
            attrs.append(f'uri="{escape(self.uri)}"')
        # Add ASCII variants if they exist
        if self._ascii_fullname:
            attrs.append(f'asciiFullname="{escape(self._ascii_fullname)}"')
        if self._ascii_initials:
            attrs.append(f'asciiInitials="{escape(self._ascii_initials)}"')
        if self._ascii_surname:
            attrs.append(f'asciiSurname="{escape(self._ascii_surname)}"')
        # Create the author tag with proper XML escaping
        return f'<author {" ".join(attrs)}/>'


@dataclass
class Date:
    """RFC XML date information."""

    year: str
    month: Optional[str] = None
    day: Optional[str] = None
    timezone: Optional[str] = None

    def to_xml(self) -> str:
        """Convert date to XML."""
        attrs = [f'year="{escape(self.year)}"']
        if self.month:
            attrs.append(f'month="{escape(self.month)}"')
        if self.day:
            attrs.append(f'day="{escape(self.day)}"')
        if self.timezone:
            attrs.append(f'timezone="{escape(self.timezone)}"')
        return f'<date {" ".join(attrs)}/>'


@dataclass
class SeriesInfo:
    """RFC XML series information."""

    name: str
    value: str
    ascii_name: Optional[str] = None
    ascii_value: Optional[str] = None
    status: Optional[str] = None
    stream: Optional[str] = None

    def to_xml(self) -> str:
        """Convert series info to XML."""
        # Convert name and value to Unicode
        unicode_name = latex_to_unicode(self.name)
        unicode_value = latex_to_unicode(self.value)
        attrs = [
            f'name="{escape(unicode_name)}"',
            f'value="{escape(unicode_value)}"',
        ]
        if self.ascii_name:
            attrs.append(f'asciiName="{escape(self.ascii_name)}"')
        if self.ascii_value:
            attrs.append(f'asciiValue="{escape(self.ascii_value)}"')
        if self.status:
            attrs.append(f'status="{escape(self.status)}"')
        if self.stream:
            attrs.append(f'stream="{escape(self.stream)}"')
        return f'<seriesInfo {" ".join(attrs)}/>'


@dataclass
class Front:
    """RFC XML front matter."""

    title: str
    authors: List[Author] = field(default_factory=list)
    date: Optional[Date] = None
    abstract: Optional[str] = None
    note: Optional[str] = None
    ascii_title: Optional[str] = None
    ascii_abstract: Optional[str] = None
    ascii_note: Optional[str] = None

    def to_xml(self) -> str:
        """Convert front matter to XML."""
        xml = ['<front>']
        attrs = []
        if self.ascii_title:
            attrs.append(f'asciiTitle="{escape(self.ascii_title)}"')
        # Convert title to Unicode
        unicode_title = latex_to_unicode(self.title)
        xml.append(f'  <title{" " + " ".join(attrs) if attrs else ""}>{escape(unicode_title)}</title>')
        # Output each author as-is
        for author in self.authors:
            xml.append(f'  {author.to_xml()}')
        if self.date:
            xml.append(f'  {self.date.to_xml()}')
        if self.abstract:
            attrs = []
            if self.ascii_abstract:
                attrs.append(f'asciiAbstract="{escape(self.ascii_abstract)}"')
            # Convert abstract to Unicode
            unicode_abstract = latex_to_unicode(self.abstract)
            xml.append(f'  <abstract{" " + " ".join(attrs) if attrs else ""}>{escape(unicode_abstract)}</abstract>')
        if self.note:
            attrs = []
            if self.ascii_note:
                attrs.append(f'asciiNote="{escape(self.ascii_note)}"')
            # Convert note to Unicode
            unicode_note = latex_to_unicode(self.note)
            xml.append(f'  <note{" " + " ".join(attrs) if attrs else ""}>{escape(unicode_note)}</note>')
        xml.append('</front>')
        return '\n'.join(xml)


@dataclass
class Reference:
    """RFC XML reference."""

    anchor: str
    front: Front
    series_info: List[SeriesInfo] = field(default_factory=list)
    target: Optional[str] = None
    status: Optional[str] = None
    organization: Optional[str] = None
    date: Optional[Date] = None
    ascii_anchor: Optional[str] = None
    ascii_target: Optional[str] = None
    ascii_organization: Optional[str] = None

    def to_xml(self) -> str:
        """Convert reference to XML."""
        attrs = [f'anchor="{escape(self.anchor)}"']
        if self.target:
            attrs.append(f'target="{escape(self.target)}"')
        if self.status:
            attrs.append(f'status="{escape(self.status)}"')
        if self.organization:
            attrs.append(f'organization="{escape(self.organization)}"')
        if self.ascii_anchor:
            attrs.append(f'asciiAnchor="{escape(self.ascii_anchor)}"')
        if self.ascii_target:
            attrs.append(f'asciiTarget="{escape(self.ascii_target)}"')
        if self.ascii_organization:
            attrs.append(f'asciiOrganization="{escape(self.ascii_organization)}"')

        xml = [f'<reference {" ".join(attrs)}>']
        xml.append(f'  {self.front.to_xml()}')
        for info in self.series_info:
            xml.append(f'  {info.to_xml()}')
        if self.date:
            xml.append(f'  {self.date.to_xml()}')
        xml.append('</reference>')
        return '\n'.join(xml) 