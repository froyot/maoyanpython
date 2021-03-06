# coding=utf-8


import codecs
import json
from pyecharts import Geo

from pyecharts.datasets.coordinates import get_coordinate

DEFAULT_GEO_TOOLTIP_FORMATTER = "{b}: {c}"

import json 

class MyGeo(Geo):

    def add(self, *args, **kwargs):
        self.__add(*args, **kwargs)
        return self

    def __add(
        self,
        name,
        attr,
        value,
        type="scatter",
        maptype="china",
        coordinate_region="中国",
        symbol_size=12,
        border_color="#111",
        geo_normal_color="#323c48",
        geo_emphasis_color="#2a333d",
        geo_cities_coords=None,
        is_roam=True,
        **kwargs
    ):
        """

        :param name:
            系列名称，用于 tooltip 的显示，legend 的图例筛选。
        :param attr:
            属性名称。
        :param value:
            属性所对应的值。
        :param type:
            图例类型，有'scatter', 'effectscatter', 'heatmap'可选。
        :param maptype:
            地图类型。 从 v0.3.2+ 起，地图已经变为扩展包，支持全国省份，全国城市，全国区县，
            全球国家等地图，具体请参考 [地图自定义篇](zh-cn/customize_map)
        :param coordinate_region:
            城市坐标所属国家。从 v0.5.7 引入，针对国际城市的地理位置的查找。默认为 `中国`。
            具体的国家/地区映射表参照 datasets/countries_regions_db.json。更多地理坐标
            信息可以参考 [数据集篇](/zh-cn/datasets)
        :param symbol_size:
            标记图形大小。
        :param border_color:
            地图边界颜色。
        :param geo_normal_color:
            正常状态下地图区域的颜色。
        :param geo_emphasis_color:
            高亮状态下地图区域的颜色。
        :param geo_cities_coords:
            用户自定义地区经纬度，类似如 {'阿城': [126.58, 45.32],} 这样的字典，当用
            于提供了该参数时，将会覆盖原有预存的区域坐标信息。
        :param is_roam:
            是否开启鼠标缩放和平移漫游。默认为 True。
            如果只想要开启缩放或者平移，可以设置成'scale'或者'move'。设置成 True 为都开启。
        :param kwargs:
        """
        emphasis_show = False
        assert len(attr) == len(value)
        kwargs.update(type="geo")
        if "tooltip_formatter" not in kwargs:
            kwargs["tooltip_formatter"] = DEFAULT_GEO_TOOLTIP_FORMATTER
        if "emphasis_show" in kwargs:
            emphasis_show = kwargs['emphasis_show']

        chart = self._get_all_options(**kwargs)

        if geo_cities_coords:
            for city_name, city_coord in geo_cities_coords.items():
                self.add_coordinate(city_name, city_coord[0], city_coord[1])

        _data = []
        for _name, _value in zip(attr, value):
            _coordinate = self.get_coordinate(
                _name, coordinate_region, raise_exception=True
            )
            _data_value = [_coordinate[0], _coordinate[1], _value]
            _data.append({"name": _name, "value": _data_value})
        self._option.update(
            geo={
                "map": maptype,
                "roam": is_roam,
                "label": {
                    "emphasis": {"show": emphasis_show, "textStyle": {"color": "#eee"}}
                },
                "itemStyle": {
                    "normal": {
                        "areaColor": geo_normal_color,
                        "borderColor": border_color,
                    },
                    "emphasis": {"areaColor": geo_emphasis_color},
                },
            }
        )
        self._option.get("legend")[0].get("data").append(name)

        chart["label"]['emphasis'].update(show = False)

        if type == "scatter":
            self._option.get("series").append(
                {
                    "type": type,
                    "name": name,
                    "coordinateSystem": "geo",
                    "symbol": chart["symbol"],
                    "symbolSize": symbol_size,
                    "data": _data,
                    "label": chart["label"],
                }
            )

        elif type == "effectScatter":
            self._option.get("series").append(
                {
                    "type": type,
                    "name": name,
                    "coordinateSystem": "geo",
                    "showEffectOn": "render",
                    "rippleEffect": chart["effect"],
                    "symbol": chart["symbol"],
                    "symbolSize": symbol_size,
                    "data": _data,
                    "label": chart["label"],
                }
            )

        elif type == "heatmap":
            self._option.get("series").append(
                {
                    "type": type,
                    "name": name,
                    "coordinateSystem": "geo",
                    "data": _data,
                }
            )

        self._add_chinese_map(maptype)
        self._config_components(**kwargs)
