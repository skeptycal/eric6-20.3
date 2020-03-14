# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2020 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing CSS styles for the Markdown preview.
"""


css_markdown = """
@media (prefers-color-scheme: light) {
    :root {
        --font-color: #000;
        --background-color: #fff;
        --alt-backgroundcolor: #f8f8f8;
        --frame-color: #333;
    }
}

@media (prefers-color-scheme: dark) {
    :root {
        --font-color: #fff;
        --background-color: #000;
        --alt-backgroundcolor: #707070;
        --frame-color: #ccc;
    }
}

html {
    background-color: var(--background-color, #fff);
}

body {
    background-color: var(--background-color, #fff);
    color: var(--font-color, #000);
    font-family: sans-serif;
    font-size:12px;
    line-height:1.7;
    word-wrap:break-word
}

body>*:first-child {
    margin-top:0 !important
}

body>*:last-child {
    margin-bottom:0 !important
}

a.absent {
    color:#c00
}

a.anchor {
    display:block;
    padding-right:6px;
    padding-left:30px;
    margin-left:-30px;
    cursor:pointer;
    position:absolute;
    top:0;
    left:0;
    bottom:0
}

a.anchor:focus {
    outline:none
}

tt, code, pre {
    font-family: Consolas, "Liberation Mono", Courier, monospace;
    font-size: 12px;
}

h1, h2, h3, h4, h5, h6 {
    margin:1em 0 6px;
    padding:0;
    font-weight:bold;
    line-height:1.7;
    cursor:text;
    position:relative
}

h1 .octicon-link, h2 .octicon-link, h3 .octicon-link, h4 .octicon-link,
h5 .octicon-link, h6 .octicon-link {
    display:none;
    color: var(--font-color, #000);
}

h1:hover a.anchor, h2:hover a.anchor, h3:hover a.anchor, h4:hover a.anchor,
h5:hover a.anchor, h6:hover a.anchor {
    text-decoration:none;
    line-height:1;
    padding-left:8px;
    margin-left:-30px;
    top:15%
}

h1:hover a.anchor .octicon-link, h2:hover a.anchor .octicon-link,
h3:hover a.anchor .octicon-link, h4:hover a.anchor .octicon-link,
h5:hover a.anchor .octicon-link, h6:hover a.anchor .octicon-link {
    display:inline-block
}

h1 tt, h1 code, h2 tt, h2 code, h3 tt, h3 code, h4 tt, h4 code,
h5 tt, h5 code, h6 tt, h6 code {
    font-size:inherit
}

h1 {
    font-size:2em;
    border-bottom:1px solid #ddd
}

h2 {
    font-size:1.6em;
    border-bottom:1px solid #eee
}

h3 {
    font-size:1.4em
}

h4 {
    font-size:1.2em
}

h5 {
    font-size:1em
}

h6 {
    color:#777;
    font-size:1em
}

p, blockquote, ul, ol, dl, table, pre {
    margin:8px 0
}

hr {
    background: rgba(216, 216, 216, 1);
    border: 0 none;
    color: #ccc;
    height: 2px;
    padding: 0;
    margin: 8px 0;
}

ul, ol {
    padding-left:15px
}

ul.no-list, ul.task-list, ol.no-list, ol.task-list {
    list-style-type:none;
}

ul ul, ul ol, ol ol, ol ul {
    margin-top:0;
    margin-bottom:0
}


dl {
    padding:0
}

dl dt {
    font-size:14px;
    font-weight:bold;
    font-style:italic;
    padding:0;
    margin-top:8px
}

dl dd {
    margin-bottom:15px;
    padding:0 8px
}

blockquote {
    border-left:4px solid #DDD;
    padding:0 8px;
    color:#777
}

blockquote>:first-child {
    margin-top:0px
}

blockquote>:last-child {
    margin-bottom:0px
}

table {
    border-collapse: collapse;
    border-spacing: 0;
    overflow:auto;
    display:block
}

table th {
    font-weight:bold
}

table th, table td {
    border:1px solid #ddd;
    padding:3px 3px
}

table tr {
    border-top:1px solid #ccc;
    background-color: var(--background-color, #fff);
}

table tr:nth-child(2n) {
    background-color:var(--alt-background-color, #f8f8f8);
}

img {
    max-width:100%;
    -moz-box-sizing:border-box;
    box-sizing:border-box
}

span.frame {
    display:block;
    overflow:hidden
}

span.frame>span {
    border:1px solid #ddd;
    display:block;
    float:left;
    overflow:hidden;
    margin:6px 0 0;
    padding:7px;
    width:auto
}

span.frame span img {
    display:block;
    float:left
}

span.frame span span {
    clear:both;
    color:var(--frame-color, #333);
    display:block;
    padding:5px 0 0
}

span.align-center {
    display:block;
    overflow:hidden;
    clear:both
}

span.align-center>span {
    display:block;
    overflow:hidden;
    margin:6px auto 0;
    text-align:center
}

span.align-center span img {
    margin:0 auto;
    text-align:center
}

span.align-right {
    display:block;
    overflow:hidden;
    clear:both
}

span.align-right>span {
    display:block;
    overflow:hidden;
    margin:6px 0 0;
    text-align:right
}

span.align-right span img {
    margin:0;
    text-align:right
}

span.float-left {
    display:block;
    margin-right:6px;
    overflow:hidden;
    float:left
}

span.float-left span {
    margin:6px 0 0
}

span.float-right {
    display:block;
    margin-left:6px;
    overflow:hidden;
    float:right
}

span.float-right>span {
    display:block;
    overflow:hidden;
    margin:6px auto 0;
    text-align:right
}

code, tt {
    margin:0;
    border:1px solid #ddd;
    background-color:var(--alt-background-color, #f8f8f8);
    border-radius:3px;
    max-width:100%;
    display:inline-block;
    overflow:auto;
    vertical-align:middle;
    line-height:1.1;
    padding:0
}

code:before, code:after, tt:before, tt:after {
    content:"\00a0"
}

code {
    white-space:nowrap
}

pre>code {
    margin:0;
    padding:0;
    white-space:pre;
    border:none;
    background:transparent
}

.highlight pre, pre {
    background-color:var(--alt-background-color, #f8f8f8);
    border:1px solid #ddd;
    font-size:12px;
    line-height:16px;
    overflow:auto;
    padding:6px 6px;
    border-radius:3px
}

pre {
    word-wrap:normal
}

pre code, pre tt {
    margin:0;
    padding:0;
    background-color:transparent;
    border:none;
    word-wrap:normal;
    max-width:initial;
    display:inline;
    overflow:initial;
    line-height:inherit
}

pre code:before, pre code:after, pre tt:before, pre tt:after {
    content:normal
}

kbd {
    border:1px solid gray;
    font-size:1.2em;
    box-shadow:1px 0 1px 0 #eee, 0 1px 0 1px #ccc, 0 2px 0 2px #444;
    -webkit-border-radius:2px;
    -moz-border-radius:2px;
    border-radius:2px;
    margin:2px 3px;
    padding:1px 5px;
    color: #000;
    background-color: #fff
}
"""


css_pygments = """
pre .hll { background-color: #ffffcc }

/* Comment */
pre .c { color: #999988; font-style: italic }

/* Error */
pre .err { color: #a61717; background-color: #e3d2d2 }

/* Keyword */
pre .k { font-weight: bold }

/* Operator */
pre .o { font-weight: bold }

/* Comment.Multiline */
pre .cm { color: #999988; font-style: italic }

/* Comment.Preproc */
pre .cp { color: #999999; font-weight: bold; font-style: italic }

/* Comment.Single */
pre .c1 { color: #999988; font-style: italic }

/* Comment.Special */
pre .cs { color: #999999; font-weight: bold; font-style: italic }

/* Generic.Deleted */
pre .gd { color: #000000; background-color: #ffdddd }

/* Generic.Emph */
pre .ge { font-style: italic }

/* Generic.Error */
pre .gr { color: #aa0000 }

/* Generic.Heading */
pre .gh { color: #999999 }

/* Generic.Inserted */
pre .gi { color: #000000; background-color: #ddffdd }

/* Generic.Output */
pre .go { color: #888888 }

/* Generic.Prompt */
pre .gp { color: #555555 }

/* Generic.Strong */
pre .gs { font-weight: bold }

/* Generic.Subheading */
pre .gu { color: #aaaaaa }

/* Generic.Traceback */
pre .gt { color: #aa0000 }

/* Keyword.Constant */
pre .kc { font-weight: bold }

/* Keyword.Declaration */
pre .kd { font-weight: bold }

/* Keyword.Namespace */
pre .kn { font-weight: bold }

/* Keyword.Pseudo */
pre .kp { font-weight: bold }

/* Keyword.Reserved */
pre .kr { font-weight: bold }

/* Keyword.Type */
pre .kt { color: #445588; font-weight: bold }

/* Literal.Number */
pre .m { color: #009999 }

/* Literal.String */
pre .s { color: #d01040 }

/* Name.Attribute */
pre .na { color: #008080 }

/* Name.Builtin */
pre .nb { color: #0086B3 }

/* Name.Class */
pre .nc { color: #445588; font-weight: bold }

/* Name.Constant */
pre .no { color: #008080 }

/* Name.Decorator */
pre .nd { color: #3c5d5d; font-weight: bold }

/* Name.Entity */
pre .ni { color: #800080 }

/* Name.Exception */
pre .ne { color: #990000; font-weight: bold }

/* Name.Function */
pre .nf { color: #990000; font-weight: bold }

/* Name.Label */
pre .nl { color: #990000; font-weight: bold }

/* Name.Namespace */
pre .nn { color: #555555 }

/* Name.Tag */
pre .nt { color: #000080 }

/* Name.Variable */
pre .nv { color: #008080 }

/* Operator.Word */
pre .ow { font-weight: bold }

/* Text.Whitespace */
pre .w { color: #bbbbbb }

/* Literal.Number.Float */
pre .mf { color: #009999 }

/* Literal.Number.Hex */
pre .mh { color: #009999 }

/* Literal.Number.Integer */
pre .mi { color: #009999 }

/* Literal.Number.Oct */
pre .mo { color: #009999 }

/* Literal.String.Backtick */
pre .sb { color: #d01040 }

/* Literal.String.Char */
pre .sc { color: #d01040 }

/* Literal.String.Doc */
pre .sd { color: #d01040 }

/* Literal.String.Double */
pre .s2 { color: #d01040 }

/* Literal.String.Escape */
pre .se { color: #d01040 }

/* Literal.String.Heredoc */
pre .sh { color: #d01040 }

/* Literal.String.Interpol */
pre .si { color: #d01040 }

/* Literal.String.Other */
pre .sx { color: #d01040 }

/* Literal.String.Regex */
pre .sr { color: #009926 }

/* Literal.String.Single */
pre .s1 { color: #d01040 }

/* Literal.String.Symbol */
pre .ss { color: #990073 }

/* Name.Builtin.Pseudo */
pre .bp { color: #999999 }

/* Name.Variable.Class */
pre .vc { color: #008080 }

/* Name.Variable.Global */
pre .vg { color: #008080 }

/* Name.Variable.Instance */
pre .vi { color: #008080 }

/* Literal.Number.Integer.Long */
pre .il { color: #009999 }

"""
