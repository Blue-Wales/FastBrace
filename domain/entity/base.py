#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : base.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 领域实体基类
"""

from pydantic import BaseModel, Field, field_validator

from infrastructure.core.enum_var import FileType
from infrastructure.utils.id_generator import SnowflakeIDGenerator


class Entity(BaseModel):
    """可变的实体基类"""

    entity_id: int = Field(default_factory=SnowflakeIDGenerator())

    @field_validator("entity_id")
    def check_entity_id(cls, value):
        if value is None:
            return cls.model_fields["entity_id"].default_factory()
        return value

    class Config:
        validate_assignment = True 
        arbitrary_types_allowed = True 

    def add_attachments(self, file_vo_list):
        """
        绑定附件
        :param file_vo_list:
        :return:
        """
        for file_vo in file_vo_list:
            if hasattr(self, FileType(file_vo.file_type).name):
                getattr(self, FileType(file_vo.file_type).name).append(file_vo.model_dump())

    def get_file_vo_list(self):
        """
        获取文件值对象列表
        :return:
        """
        file_vo_list = []
        for key in self.__dict__:
            if key in FileType.__members__:
                for file_vo in getattr(self, key):
                    file_vo_list.append(
                        {
                            "master_id": self.entity_id,
                            "file_type": FileType[key].value,
                            "file_path": file_vo.get("file_path"),
                            "file_name": file_vo.get("file_name"),
                            "extra_info": file_vo.get("extra_info", None),
                        }
                    )
        return file_vo_list

    def get_file_vo_empty_list(self):
        """
        获取空文件值对象列表
        :return:
        """
        file_vo_list = []
        for key in self.__dict__:
            if key in FileType.__members__ and (
                not getattr(self, key) or len(getattr(self, key)) == 0
            ):
                file_vo_list.append(
                    {
                        "master_id": self.entity_id,
                        "file_type": FileType[key].value,
                    }
                )
        return file_vo_list

    def get_file_type_list(self):
        """
        获取文件类型列表
        :return:
        """
        file_type_list = []
        for key in self.__dict__:
            if key in FileType.__members__:
                file_type_list.append(FileType[key].value)
        return file_type_list


if __name__ == "__main__":
    pass
