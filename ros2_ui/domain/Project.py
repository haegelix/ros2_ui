import dataclasses
from dataclass_dict_convert import dataclass_dict_convert
from typing import List

from ros2_ui.domain.Node import Publisher, Subscriber


@dataclass_dict_convert
@dataclasses.dataclass
class ProjectInfo:
    """
    Holds metadata about a project.
    """
    package_name: str  # Name of the package
    version: str  # Version of the package
    description: str  # Description of the package
    maintainer_mail: str  # Email address of the packages maintainer
    maintainer: str  # Name of the packages maintainer
    license: str  # Licence of the package


@dataclass_dict_convert
@dataclasses.dataclass
class ProjectDependencies:
    test_depends: List[str]  # Dependencies to be used in testing of the package
    exec_depends: List[str]  # Dependencies to be used in execution of the package


@dataclass_dict_convert
@dataclasses.dataclass
class Project:
    project_info: ProjectInfo
    project_dependencies: ProjectDependencies
    pubs: List[Publisher]
    subs: List[Subscriber]
