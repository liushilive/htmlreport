"""
Copyright 2017 刘士

Licensed under the Apache License, Version 2.0 (the "License"): you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""


class TemplateMixin(object):
    # 定义生成HTML结果文件所需要的模板。

    STATUS_cn = {
        0: "通过",
        1: "失败",
        2: "错误",
        3: "跳过",
    }
    STATUS_en = {
        0: "pass",
        1: "fail",
        2: "error",
        3: "skip",
    }

    DEFAULT_TITLE = "测试报告"
    DEFAULT_TITLE_en = "Test Results"
    DEFAULT_DESCRIPTION = "测试描述"
    DEFAULT_DESCRIPTION_en = "Test Description"

    HTML_TMPL = r"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <title>{title}</title>
    <meta name="generator" content="{generator}"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <style type="text/css" media="screen">{stylesheet}</style>
    <script language="javascript" type="text/javascript">{js}</script>
</head>

<body onload="load()">
<div id="wrapper" class="lang-{lang}">
    <div id="lang">
        <ul>
            <li>
                <a href="#cn" id="lang-cn" title="简体中文">cn</a>
            </li>
            <li>
                <a href="#en" id="lang-en" title="English">en</a>
            </li>
        </ul>
    </div>
    {heading} {log} {report} {ending}
    <div id="popup">
        <div class="bg">
            <img src="" alt=""/>
        </div>
    </div>
</div>
</body>

</html>
"""

    JS = r"""output_list = Array();

function addClass(e, c) {
    if (!isClass(e, c)) {
        if (e.className) {
            e.className = e.className + " " + c;
        } else {
            e.className = c;
        }
    }
}

function delClass(e, c) {
    if (isClass(e, c)) {
        // r = '/(?:^|\s)' + c + '(?!\S)/g';
        r = new RegExp('(?:^|\\s)' + c + '(?!\\S)', 'g');
        e.className = e.className.replace(r, '');
    }
}

function isClass(e, c) {
    r = new RegExp('(?:^|\\s)' + c + '(?!\\S)');
    return e.className.match(r);
}

function showCase(level) {
    trs = document.getElementsByTagName("tr");
    for (var i = 0; i < trs.length; i++) {
        tr = trs[i];
        id = tr.id;
        if (id.substr(0, 2) === "st") {
            if (level === 4 || level === 3) {
                delClass(tr, 'hiddenRow');
            } else {
                addClass(tr, 'hiddenRow');
            }
        }
        if (id.substr(0, 2) === "ft") {
            if (level === 4 || level === 2) {
                delClass(tr, 'hiddenRow');
            } else {
                addClass(tr, 'hiddenRow');
            }
        }
        if (id.substr(0, 2) === "pt") {
            if (level === 4 || level === 1) {
                delClass(tr, 'hiddenRow');
            } else {
                addClass(tr, 'hiddenRow');
            }
        }
        if (id.substr(0, 2) === "et") {
            if (level === 4 || level === 5 || level === 2) {
                delClass(tr, 'hiddenRow');
            } else {
                addClass(tr, 'hiddenRow');
            }
        }
        if (id.substr(0, 4) === "div_") {
            addClass(tr, 'hiddenRow');
        }
    }
}

function showClassDetail(cid, count) {
    var id_list = Array(count);
    var toHide = 1;
    for (var i = 0; i < count; i++) {
        tid0 = "t" + cid.substr(1) + "." + (i + 1);
        tid = "f" + tid0;
        tr = document.getElementById(tid);
        if (!tr) {
            tid = "p" + tid0;
            tr = document.getElementById(tid);
            if (!tr) {
                tid = "e" + tid0;
                tr = document.getElementById(tid);
                if (tr === null) {
                    tid = "s" + tid0;
                    tr = document.getElementById(tid);
                }
            }
        }
        id_list[i] = tid;
        if (tr.className) {
            toHide = 0;
        }
    }
    for (var i = 0; i < count; i++) {
        tid = id_list[i];
        if (toHide && tid.indexOf("p") !== -1) {
            addClass(document.getElementById(tid), 'hiddenRow');
        } else {
            delClass(document.getElementById(tid), 'hiddenRow');
        }
    }
    trs = document.getElementsByTagName("tr");
    for (var i = 0; i < trs.length; i++) {
        tr = trs[i]
        id = tr.id
        if (id.substr(0, 4) === "div_") {
            addClass(tr, 'hiddenRow');
        }
    }
}

function showTestDetail(div_id, count, b) {
    var details_divs = document.getElementsByName(div_id);
    for (var j = 0; j < details_divs.length; j++) {
        var details_div = details_divs[j];
        if (isClass(details_div, 'hiddenRow')) {
            delClass(details_div, 'hiddenRow');
        } else {
            addClass(details_div, "hiddenRow");
        }
    }
    for (var i = 1; i <= count; i++) {
        var details_divs = document.getElementsByName(div_id + '.' + i);
        for (var j = 0; j < details_divs.length; j++) {
            var details_div = details_divs[j]
            if (details_div !== undefined) {
                if (b && isClass(details_div, 'hiddenRow')) {
                    delClass(details_div, 'hiddenRow');
                } else {
                    addClass(details_div, "hiddenRow");
                }
            }
        }
    }
}

function html_escape(s) {
    s = s.replace(/&/g, "&amp;");
    s = s.replace(/</g, "&lt;");
    s = s.replace(/>/g, "&gt;");
    return s;
}

function load() {
    var el_wrapper = document.getElementById('wrapper');
    document.getElementById('lang-cn').onclick = function () {
        el_wrapper.className = 'lang-cn';
    };
    document.getElementById('lang-en').onclick = function () {
        el_wrapper.className = 'lang-en';
    };

    var h = (location.hash || '').replace(/#/, '');
    var nav_lang;
    if (h === 'cn' || h === 'en') {
        el_wrapper.className = 'lang-' + h;
    }

    var imgs = document.getElementsByClassName("pic");
    var lens = imgs.length;
    var popup = document.getElementById("popup");
    for (var i = 0; i < lens; i++) {
        imgs[i].onclick = function (event) {
            event = event || window.event;
            var target = document.elementFromPoint(event.clientX, event.clientY);
            showBig(target.src, target.title, target.alt);
        };
    }
    popup.onclick = function () {
        popup.getElementsByTagName("img")[0].src = "";
        popup.getElementsByTagName("img")[0].title = "";
        popup.getElementsByTagName("img")[0].alt = "";
        popup.style.display = "none";
        popup.style.zIndex = "-1";
    };

    function showBig(src, title, alt) {
        popup.getElementsByTagName("img")[0].src = src;
        popup.getElementsByTagName("img")[0].title = title;
        popup.getElementsByTagName("img")[0].alt = alt;
        popup.style.display = "block";
        popup.style.zIndex = "999999";
    }
}
"""

    STYLESHEET_TMPL = r"""body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
  font-size: 14px;
}

pre {
  word-wrap: break-word;
  word-break: break-all;
  overflow: auto;
  white-space: pre-wrap
}

h1 {
  font-size: 16pt;
  color: gray
}

.heading {
  margin-top: 0;
  margin-bottom: 1ex
}

.heading .attribute {
  margin-top: 1ex;
  margin-bottom: 0
}

.heading .description {
  margin-top: 4ex;
  margin-bottom: 6ex
}

a.popup_link:hover {
  color: red
}

.popup_window {
  display: block;
  position: relative;
  left: 0;
  top: 0;
  padding: 10px;
  background-color: #E6E6D6;
  text-align: left;
  font-size: 13px
}

.popup_retry_window {
  padding-left: 50px;
}

#show_detail_line {
  margin-top: 3ex;
  margin-bottom: 1ex
}

#result_table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #777
}

#header_row {
  color: #fff;
  background-color: #777
}

#result_table td {
  border: 1px solid #777;
  padding: 2px;
}

#result_table td:nth-child(n+2) {
  min-width: 70px;
  width: 100%
}

#result_table td:nth-child(n+3) {
  text-align: center;
}

#result_table td:first-of-type {
  text-align: center;
  min-width: 60px;
}

#total_row {
  font-weight: bold
}

.passClass,
.failClass,
.errorClass,
.skipClass {
  font-weight: bold
}

.passCase {
  background-color: #d0e9c6
}

.failCase {
  background-color: #ebcccc
}

.errorCase {
  background-color: #faf2cc
}

.skipCase {
  background-color: #c4e3f3
}

.hiddenRow {
  display: none
}

.testcase {
  margin-left: 2em
}

#popup {
  position: fixed;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  text-align: center;
  display: none
}

#popup .bg {
  background-color: rgba(0, 0, 0, .5);
  width: 100%;
  height: 100%
}

@media \0screen\,screen\9 {
  #popup .bg {
    background-color: #000;
    filter: Alpha(opacity=50);
    position: static
  }

  #popup .bg img {
    position: relative
  }
}

#popup img {
  max-width: 100%;
  max-height: 100%;
  margin: auto;
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
}

img.pic {
  cursor: pointer;
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: 100%;
}

#wrapper {
  margin: 0 auto;
  border-top: solid 2px #666;
}

#wrapper .lang-en {
  display: none;
}

#wrapper.lang-cn p.lang-cn {
  display: block;
}

#wrapper.lang-cn span.lang-cn {
  display: inline;
}

#wrapper.lang-cn .lang-en {
  display: none;
}

#wrapper.lang-en .lang-cn {
  display: none;
}

#wrapper.lang-en p.lang-en {
  display: block;
}

#wrapper.lang-en span.lang-en {
  display: inline;
}

#lang ul {
  float: right;
  margin: 0;
  padding: 2px 10px 4px 10px;
  background: #666;
  border-radius: 0 0 4px 4px;
  list-style: none;
}

#lang li {
  margin: 0;
  float: left;
  padding: 0 5px;
}

#lang li a {
  display: block;
  width: 24px;
  height: 24px;
  text-indent: -4em;
  overflow: hidden;
  background: transparent url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAAHiSURBVHja1Ja/jtNAEMZ/Y2/icBdxXAMSEu/A1dBR0NJQ8CS8AQ0tb4CQgEegPgQFOh7ixJUX4vgSx96ZoUgOO3+KRDgFX7Or0Wg+f7PzeVfcnUMi4cA4OIEAARgAvY5r10AZgOGvl69Gkm4Xk9w3fJTg9f4MDz9+OA3AsSTC4OmThaQE3Bp9w+eRmy+hie2I8us3gOMABFNFkjlW5PTPIvOLAO7YVMjfC/Sd4YuK4nOGuyMiABv7v6pP7mKmACEAeK1YPuPoWU52FgkPUiaf+ngFDjCD+Q/Fproo1vrSbUPuvR4eF7kBwDRi4ynlzxkyUMrvKTZabbrPFb9Jd2qPh7BK4DGiRYFeTJmdC8nAsVKaUes72eOK6Xm2G0GaYhpXCTzPsXEBgOZN8unrktHbAddvAKrdCESwqmoItI74eILlkw0bjt4Zltdg+5hL8NhSYLGmurrCxuPN7Mv951+LAh1kLQWxBlUw68bDGtEqaStQiB0SRMWlbh1yXWPu+MIc/wzTiC0dslBQR0TArfWPwJdr21KyttLKaeJijvmaD0gTMF/z57pPt8W37E1xaylwU0iE5OhON2fgjreMVmuMXC/ntus7QYAT4BFwr+Piv4HL2xstu21Xh4jAXP77V8WfAQAixA0rudAk0AAAAABJRU5ErkJggg==") no-repeat 50% 50%;
}

#lang li a#lang-en {
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAAIWSURBVHja1JY/SBthGIefu1xqS6K20KFDy0kopUiHmphIByUZotRAIZOTWZzFpYtbB0uh6KJTIdQhi9pBSwmmCOpgoUSKFItTh4AU6tCr16Rn5P58XZocDrlYuAz9wfHAcbzv9/2+932/k4QQdFIyHVbHE0iAAlwFgj7HNoG6AoRzudc/A4F/28yL2l7bb269yd9QgJAsS8zMjFIufyWRuHspXqtbnsHrH8oAIQlQJyfzlaGhCNFohJ2dI1Kp/iZ3d49IJvsvvJckmJ197JlACIEsy30KgGUJBgcjFIufSacfsLnpza2tL/x4+qx15fR0Uz84hL8HjG1blEqHJJP9bGx8IpMZ8CSAMIzWq1cUhO24CSzLYWTkPisrH8lm46yuenN9fZ+br156WmRZFgQLjR3YrK2VyWSiFAp7TEw88iTAyZNca4t6e6h/P3EbzTRtxscfks9vk83G27JaPcOuVls/v6o4pltlajo9L1KpebG8vC9isbm2jMXmRDsZhiEAVWn4NTU1ysJCkenpMRYXS55cWnrPcSThUUVhzrquNEeFOjz8vOI4CrXa+aU7+d3p29YJusMYwQD3Drb7AFRd14Xf0nXdtehbfAxdkhG13/5M0HCImiTcPhC2BVIAHMefOWrbCNxYqqZpvlukaVrTIrNye4CK1JH7xpSAXuAOcN3n4KfAceNG62qch4+ygHPpv/+r+DMAXV79BpyNnBoAAAAASUVORK5CYII=");
}

.figure_ul {
  text-align: center;
  padding: 0;
}

.figure_li {
  width: 30em;
  list-style: none;
  display: inline-block;
  vertical-align: baseline;
}

tr {
  height: 2em;
}"""

    HEADING_TMPL = r"""<div class='heading'>
  <h1>{title}</h1>
  <p class='attribute'>
    <strong>
      <span class="lang-cn">启动时间：</span>
      <span class="lang-en">Start Time:</span>
    </strong> {startTime}
  </p>
  <p class='attribute'>
    <strong>
      <span class="lang-cn">结束时间：</span>
      <span class="lang-en">End Time:</span>
    </strong> {endTime}
  </p>
  <p class='attribute'>
    <strong>
      <span class="lang-cn">运行时长：</span>
      <span class="lang-en">Duration:</span>
    </strong> {duration}
  </p>
  <p class='attribute'>
    <strong>
      <span class="lang-cn">结果：</span>
      <span class="lang-en">Status:</span>
    </strong>
    <span class="lang-cn">合计：</span>
    <span class="lang-en">Total:</span>{total}&nbsp;&nbsp;&nbsp;&nbsp;
    <span class="lang-cn">通过：</span>
    <span class="lang-en">Passed:</span>{Pass}&nbsp;&nbsp;&nbsp;&nbsp;
    <span class="lang-cn">失败：</span>
    <span class="lang-en">Failed:</span>{fail}&nbsp;&nbsp;&nbsp;&nbsp;
    <span class="lang-cn">错误：</span>
    <span class="lang-en">Error:</span>{error}&nbsp;&nbsp;&nbsp;&nbsp;
    <span class="lang-cn">跳过：</span>
    <span class="lang-en">Skipped:</span>{skip}&nbsp;&nbsp;&nbsp;&nbsp;
  </p>
  <p class='description'>{description}</p>
</div>"""

    REPORT_TMPL = r"""<p id='show_detail_line'>筛选
    <a href='javascript:showCase(0)'>
        <span class="lang-cn">摘要</span>
        <span class="lang-en">Summary</span>
    </a>
    <a href='javascript:showCase(1)'>
        <span class="lang-cn">通过</span>
        <span class="lang-en">Pass</span>
    </a>
    <a href='javascript:showCase(2)'>
        <span class="lang-cn">失败</span>
        <span class="lang-en">Fail</span>
    </a>
    <a href='javascript:showCase(5)'>
        <span class="lang-cn">异常</span>
        <span class="lang-en">Error</span>
    </a>
    <a href='javascript:showCase(3)'>
        <span class="lang-cn">跳过</span>
        <span class="lang-en">Skip</span>
    </a>
    <a href='javascript:showCase(4)'>
        <span class="lang-cn">全部</span>
        <span class="lang-en">All</span>
    </a>
</p>
<table id='result_table'>
    <tr id='header_row'>
        <th>
            <span class="lang-cn">序号</span>
            <span class="lang-en">NO</span>
        </th>
        <th>
            <span class="lang-cn">测试组/测试用例</span>
            <span class="lang-en">Test Group/Test case</span>
        </th>
        <th>
            <span class="lang-cn">计数</span>
            <span class="lang-en">Count</span>
        </th>
        <th>
            <span class="lang-cn">通过</span>
            <span class="lang-en">Passed</span>
        </th>
        <th>
            <span class="lang-cn">失败</span>
            <span class="lang-en">Failed</span>
        </th>
        <th>
            <span class="lang-cn">错误</span>
            <span class="lang-en">Erroneous</span>
        </th>
        <th>
            <span class="lang-cn">跳过</span>
            <span class="lang-en">Skipped</span>
        </th>
        <th>
            <span class="lang-cn">统计</span>
            <span class="lang-en">Statistics</span>
        </th>
        <th>
            <span class="lang-cn">重试</span>
            <span class="lang-en">Tries</span>
        </th>
        <th>
            <span class="lang-cn">查看</span>
            <span class="lang-en">View</span>
        </th>
    </tr>
    {test_list}
    <tr id='total_row'>
        <td>&nbsp;</td>
        <td>
            <span class="lang-cn">合计</span>
            <span class="lang-en">Total</span>
        </td>
        <td>{count}</td>
        <td class="passCase">{Pass}</td>
        <td class="failCase">{fail}</td>
        <td class="errorCase">{error}</td>
        <td class="skipCase">{skip}</td>
        <td style="text-align:right;">{statistics:.2%}</td>
        <td>{tries}</td>
        <td>&nbsp;</td>
    </tr>
</table>
"""

    REPORT_CLASS_TMPL = r"""<tr class='{style}'>
    <td>{cid}</td>
    <td>{desc}</td>
    <td>{count}</td>
    <td class="passCase">{Pass}</td>
    <td class="failCase">{fail}</td>
    <td class="errorCase">{error}</td>
    <td class="skipCase">{skip}</td>
    <td style="text-align:right;">{statistics:.2%}</td>
    <td>{tries}</td>
    <td>
        <a href="javascript:showClassDetail('{cid}',{count})">
            <span class="lang-cn">细节</span>
            <span class="lang-en">Detail</span>
        </a>
    </td>
</tr>
"""

    REPORT_TEST_WITH_OUTPUT_TMPL = r"""<tr id='{tid}'>
<td>{tid}</td>
    <td class='{style}' colspan='7'>
        <div class='testcase'>{desc}</div>
    </td>
    <td class='{style}'>
        <div class='testcase' style="margin-left: auto;">{tries}</div>
    </td>
    <td class='{style}' align='center'>
        <a class="popup_link" onfocus='this.blur();' href="javascript:showTestDetail('div_{tid1}',{count}, false)">
            <span class="lang-cn">{status_cn}</span>
            <span class="lang-en">{status_en}</span>
        </a>
    </td>
</tr>
"""

    REPORT_TEST_WITH_OUTPUT_SUB_RETRY_TMPL = """<tr id='div_{tid}.{r}' name='div_{tid}' class="hiddenRow">
    <td>{tid}.{r}</td>
    <td colspan='7' class='{style}'>
        <div class='popup_retry_window'>
            <span class="lang-cn"> 第 {n} 次尝试 </span>
            <span class="lang-en"> Try {n} </span>
        </div>
    </td>
    <td class='{style}' align='center'>
        <a class="popup_link" onfocus='this.blur();'
           href="javascript:showTestDetail('div_{tid}.{r}',0, true)">
            <span class="lang-cn">{status_cn}</span>
            <span class="lang-en">{status_en}</span>
        </a>
    </td>
</tr>"""

    REPORT_TEST_WITH_OUTPUT_SUB_TMPL = """<tr id='div_S_{tid}.{r}' name='div_{tid}.{r}' class="hiddenRow">
    <td colspan='10'>
        <div class="popup_window">
            <div style='text-align: right; color:red;cursor:pointer'
                 onclick="document.getElementById('div_S_{tid}.{r}').className = 'hiddenRow'">
                <a onfocus='this.blur();'>[x]</a>
            </div>
            <pre>{script}</pre>
            <div><ul class='figure_ul'>{img}<ul></div>
        </div>
    </td>
</tr>"""

    REPORT_TEST_OUTPUT_TMPL = r"""{id}:
{output}
"""

    ENDING_TMPL = r"""<div id='ending'>&nbsp;</div>"""

    REPORT_LOG_FILE_TMPL = r"""<a href='{log_file}'>
    <span class="lang-cn">下载日志文件</span>
    <span class="lang-en">Download log file</span>
</a>
"""

    REPORT_IMG_TMPL = r"""<li class="figure_li">
    <figure>
        <img class="pic" src='{img_src}' title='{alt}' alt='{title}'/>
    </figure>
    {title}
</li>
"""
