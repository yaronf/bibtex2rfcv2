"""RFC XML v3 reference models for BibTeX to RFC conversion."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
from xml.sax.saxutils import escape


class ReferenceStatus(str, Enum):
    """RFC XML reference status values."""

    INFORMATIONAL = "informational"
    STANDARDS_TRACK = "standards-track"
    EXPERIMENTAL = "experimental"
    HISTORIC = "historic"
    UNKNOWN = "unknown"


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

    def to_xml(self) -> str:
        """Convert author to XML."""
        attrs = [f'fullname="{escape(self.fullname)}"']
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
        if self.ascii_fullname:
            attrs.append(f'asciiFullname="{escape(self.ascii_fullname)}"')
        if self.ascii_initials:
            attrs.append(f'asciiInitials="{escape(self.ascii_initials)}"')
        if self.ascii_surname:
            attrs.append(f'asciiSurname="{escape(self.ascii_surname)}"')
        if self.ascii_organization:
            attrs.append(f'asciiOrganization="{escape(self.ascii_organization)}"')
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
        attrs = [
            f'name="{escape(self.name)}"',
            f'value="{escape(self.value)}"',
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
class Format:
    """RFC XML format information."""

    type: str
    target: Optional[str] = None
    octets: Optional[str] = None
    ascii_type: Optional[str] = None
    ascii_target: Optional[str] = None

    def to_xml(self) -> str:
        """Convert format to XML."""
        attrs = [f'type="{escape(self.type)}"']
        if self.target:
            attrs.append(f'target="{escape(self.target)}"')
        if self.octets:
            attrs.append(f'octets="{escape(self.octets)}"')
        if self.ascii_type:
            attrs.append(f'asciiType="{escape(self.ascii_type)}"')
        if self.ascii_target:
            attrs.append(f'asciiTarget="{escape(self.ascii_target)}"')
        return f'<format {" ".join(attrs)}/>'


@dataclass
class Annotation:
    """RFC XML annotation information."""

    text: str
    anchor: Optional[str] = None
    ascii_text: Optional[str] = None

    def to_xml(self) -> str:
        """Convert annotation to XML."""
        attrs = []
        if self.anchor:
            attrs.append(f'anchor="{escape(self.anchor)}"')
        if self.ascii_text:
            attrs.append(f'asciiText="{escape(self.ascii_text)}"')
        return f'<annotation{" " + " ".join(attrs) if attrs else ""}>{escape(self.text)}</annotation>'


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
        xml.append(f'  <title{" " + " ".join(attrs) if attrs else ""}>{escape(self.title)}</title>')
        for author in self.authors:
            xml.append(f'  {author.to_xml()}')
        if self.date:
            xml.append(f'  {self.date.to_xml()}')
        if self.abstract:
            attrs = []
            if self.ascii_abstract:
                attrs.append(f'asciiAbstract="{escape(self.ascii_abstract)}"')
            xml.append(f'  <abstract{" " + " ".join(attrs) if attrs else ""}>{escape(self.abstract)}</abstract>')
        if self.note:
            attrs = []
            if self.ascii_note:
                attrs.append(f'asciiNote="{escape(self.ascii_note)}"')
            xml.append(f'  <note{" " + " ".join(attrs) if attrs else ""}>{escape(self.note)}</note>')
        xml.append('</front>')
        return '\n'.join(xml)


@dataclass
class Reference:
    """RFC XML reference."""

    anchor: str
    front: Front
    series_info: List[SeriesInfo] = field(default_factory=list)
    formats: List[Format] = field(default_factory=list)
    annotations: List[Annotation] = field(default_factory=list)
    target: Optional[str] = None
    status: Optional[ReferenceStatus] = None
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
            attrs.append(f'status="{self.status.value}"')
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
        for fmt in self.formats:
            xml.append(f'  {fmt.to_xml()}')
        for annotation in self.annotations:
            xml.append(f'  {annotation.to_xml()}')
        xml.append('</reference>')
        return '\n'.join(xml)


@dataclass
class ReferenceGroup:
    """RFC XML reference group."""

    anchor: str
    references: List[Reference] = field(default_factory=list)
    title: Optional[str] = None
    ascii_anchor: Optional[str] = None
    ascii_title: Optional[str] = None

    def to_xml(self) -> str:
        """Convert reference group to XML."""
        attrs = [f'anchor="{escape(self.anchor)}"']
        if self.title:
            attrs.append(f'title="{escape(self.title)}"')
        if self.ascii_anchor:
            attrs.append(f'asciiAnchor="{escape(self.ascii_anchor)}"')
        if self.ascii_title:
            attrs.append(f'asciiTitle="{escape(self.ascii_title)}"')

        xml = [f'<referencegroup {" ".join(attrs)}>']
        for ref in self.references:
            xml.append(f'  {ref.to_xml()}')
        xml.append('</referencegroup>')
        return '\n'.join(xml)


@dataclass
class References:
    """RFC XML references section."""

    references: List[Reference] = field(default_factory=list)
    reference_groups: List[ReferenceGroup] = field(default_factory=list)
    title: Optional[str] = None
    ascii_title: Optional[str] = None

    def to_xml(self) -> str:
        """Convert references section to XML."""
        attrs = []
        if self.title:
            attrs.append(f'title="{escape(self.title)}"')
        if self.ascii_title:
            attrs.append(f'asciiTitle="{escape(self.ascii_title)}"')

        xml = [f'<references {" ".join(attrs)}>']
        for ref in self.references:
            xml.append(f'  {ref.to_xml()}')
        for group in self.reference_groups:
            xml.append(f'  {group.to_xml()}')
        xml.append('</references>')
        return '\n'.join(xml) 