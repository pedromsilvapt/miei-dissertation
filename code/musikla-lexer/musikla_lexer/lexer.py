from pygments.lexer import RegexLexer, bygroups
from pygments.token import *

import re

__all__=['MusiklaLexer']

class MusiklaLexer(RegexLexer):
    name = 'Musikla'
    aliases = ['musikla']
    filenames = ['*.mkl']
    flags = re.MULTILINE | re.UNICODE

    tokens = {
        'root' : [
            (u'(fun)(?=[ \\t({})])', bygroups(Keyword), 'statement__1'),
            (u'(@python)', bygroups(Keyword), 'statement__2'),
            (u'(#.*)', bygroups(Comment)),
            (u'(\\{)', bygroups(Punctuation), 'codeblock__1'),
            (u'(@keyboard)', bygroups(Keyword), 'keyboard__1'),
            (u'(@py)([ \\t]*\\{)', bygroups(Keyword, Punctuation), 'expression__1'),
            (u'(=>|<=|>=|==|!=|[=\\*\\|\\+\\-\\/]|>=)', bygroups(Keyword.Pseudo)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*(?=\\())', bygroups(Name.Function)),
            (u'(fun|and|or|not|if|then|else|for|while|in|notin|is|isnot|none|return|ref|expr)(?=[ \\t({}),;+\\-*/])', bygroups(Keyword)),
            (u'(true|false)', bygroups(Number)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)\\s+(?=\\=))', bygroups(Number)),
            (u'([\\^\\~]{0,2}[a-gA-GrR](\\\'|,)*[Mm]?([0-9]*)(/[0-9]+)?)', bygroups(Literal)),
            (u'(([vV][0-9]+)|([lL]([0-9]*)(/[0-9]+)?)|([tT][0-9]+)|([sS]([0-9]*)(/[0-9]+)?))', bygroups(Literal)),
            (u'(::)((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))', bygroups(Keyword.Pseudo, Name.Function)),
            (u'(\\\")', bygroups(String), 'expression__2'),
            (u'(\\\')', bygroups(String), 'expression__3'),
            (u'([\\(\\)\\{\\}\\[\\]])', bygroups(Punctuation)),
            (u'(\\$(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\:(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\b\\d+)', bygroups(Number)),
            (u'([;,])', bygroups(Punctuation)),
            (u'([^\\s\\n\\r])', bygroups(Generic.Error)),
            ('(\n|\r|\r\n)', String),
            ('.', String),
        ], 
        'codeblock__1' : [
            (u'(fun)(?=[ \\t({})])', bygroups(Keyword), 'statement__1'),
            (u'(@python)', bygroups(Keyword), 'statement__2'),
            (u'(#.*)', bygroups(Comment)),
            (u'(\\{)', bygroups(Punctuation), 'codeblock__1'),
            (u'(@keyboard)', bygroups(Keyword), 'keyboard__1'),
            (u'(@py)([ \\t]*\\{)', bygroups(Keyword, Punctuation), 'expression__1'),
            (u'(=>|<=|>=|==|!=|[=\\*\\|\\+\\-\\/]|>=)', bygroups(Keyword.Pseudo)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*(?=\\())', bygroups(Name.Function)),
            (u'(fun|and|or|not|if|then|else|for|while|in|notin|is|isnot|none|return|ref|expr)(?=[ \\t({}),;+\\-*/])', bygroups(Keyword)),
            (u'(true|false)', bygroups(Number)),
            (u'([0-9a-zA-Z+ \\t]+(?=:))', bygroups(String)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)\\s+(?=\\=))', bygroups(Number)),
            (u'([\\^\\~]{0,2}[a-gA-GrR](\\\'|,)*[Mm]?([0-9]*)(/[0-9]+)?)', bygroups(Literal)),
            (u'(([vV][0-9]+)|([lL]([0-9]*)(/[0-9]+)?)|([tT][0-9]+)|([sS]([0-9]*)(/[0-9]+)?))', bygroups(Literal)),
            (u'(::)((?:[a-zA-Z\\\\\\_][a-zA-Z0-9\\\\\\_]*))', bygroups(Keyword.Pseudo, Name.Function)),
            (u'(\\\")', bygroups(String), 'expression__2'),
            (u'(\\\')', bygroups(String), 'expression__3'),
            (u'([\\(\\)\\{\\}\\[\\]])', bygroups(Punctuation)),
            (u'(\\$(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\:(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\b\\d+)', bygroups(Number)),
            (u'([;,])', bygroups(Punctuation)),
            (u'([^\\s\\n\\r])', bygroups(Generic.Error)),
            ('(\n|\r|\r\n)', String),
            ('.', String),

            (u"(\\})", bygroups(Punctuation), "#pop")
        ], 
        'expression__1' : [
            ('(\n|\r|\r\n)', Generic),
            (u"(\\})", bygroups(Punctuation), "#pop"),
            ('.', Generic)
        ],
        'expression__2' : [
            ('(\n|\r|\r\n)', String),
            (u"(\\\")", bygroups(String), "#pop"),
            ('.', String)
        ], 
        'expression__3' : [
            ('(\n|\r|\r\n)', String),
            (u"(\\')", bygroups(String), "#pop"),
            ('.', String)
        ], 
        'keyboard__1' : [
            (u'([a-zA-Z]+)', bygroups(Number)),
            (u'(\\()', bygroups(Punctuation), 'keyboard__2'),
            (u'(\\{)', bygroups(Punctuation), 'codeblock__1'),
            ('(\n|\r|\r\n)', String),
            (u"(\\})", bygroups(Punctuation), "#pop"),
            ('.', String),
        ], 
        'keyboard__2' : [
            (u'(\\{)', bygroups(Punctuation), 'codeblock__1'),
            (u'(@keyboard)', bygroups(Keyword), 'keyboard__1'),
            (u'(@py)([ \\t]*\\{)', bygroups(Keyword, Punctuation), 'expression__1'),
            (u'(=>|<=|>=|==|!=|[=\\*\\|\\+\\-\\/]|>=)', bygroups(Keyword.Pseudo)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*(?=\\())', bygroups(Name.Function)),
            (u'(fun|and|or|not|if|then|else|for|while|in|notin|is|isnot|none|return|ref|expr)(?=[ \\t({}),;+\\-*/])', bygroups(Keyword)),
            (u'(true|false)', bygroups(Number)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)\\s+(?=\\=))', bygroups(Number)),
            (u'([\\^\\~]{0,2}[a-gA-GrR](\\\'|,)*[Mm]?([0-9]*)(/[0-9]+)?)', bygroups(Literal)),
            (u'(([vV][0-9]+)|([lL]([0-9]*)(/[0-9]+)?)|([tT][0-9]+)|([sS]([0-9]*)(/[0-9]+)?))', bygroups(Literal)),
            (u'(::)((?:[a-zA-Z\\\\\\_][a-zA-Z0-9\\\\\\_]*))', bygroups(Keyword.Pseudo, Name.Function)),
            (u'(\\\")', bygroups(String), 'expression__2'),
            (u'(\\\')', bygroups(String), 'expression__3'),
            (u'([\\(\\)\\{\\}\\[\\]])', bygroups(Punctuation)),
            (u'(\\$(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\:(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\b\\d+)', bygroups(Number)),
            ('(\n|\r|\r\n)', String),
            (u"(\\))", bygroups(Punctuation), "#pop"),
            ('.', String)
        ], 
        'keyboard__3' : [
            (u'(#.*)', bygroups(Comment)),
            (u'(\\[)', bygroups(Punctuation), 'keyboard_body__1'),
            (u'(\\:)', bygroups(Punctuation), 'keyboard_body__2'),
            (u'(\\{)', bygroups(Punctuation), 'codeblock__1'),
            ('(\n|\r|\r\n)', String),
            (u"(\\})", bygroups(Punctuation), "#pop"),
            ('.', String)
        ], 
        'keyboard_body__1' : [
            (u'(\\{)', bygroups(Punctuation), 'codeblock__1'),
            (u'(@keyboard)', bygroups(Keyword), 'keyboard__1'),
            (u'(@py)([ \\t]*\\{)', bygroups(Keyword, Punctuation), 'expression__1'),
            (u'(=>|<=|>=|==|!=|[=\\*\\|\\+\\-\\/]|>=)', bygroups(Keyword.Pseudo)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*(?=\\())', bygroups(Name.Function)),
            (u'(fun|and|or|not|if|then|else|for|while|in|notin|is|isnot|none|return|ref|expr)(?=[ \\t({}),;+\\-*/])', bygroups(Keyword)),
            (u'(true|false)', bygroups(Number)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)\\s+(?=\\=))', bygroups(Number)),
            (u'([\\^\\~]{0,2}[a-gA-GrR](\\\'|,)*[Mm]?([0-9]*)(/[0-9]+)?)', bygroups(Literal)),
            (u'(([vV][0-9]+)|([lL]([0-9]*)(/[0-9]+)?)|([tT][0-9]+)|([sS]([0-9]*)(/[0-9]+)?))', bygroups(Literal)),
            (u'(::)((?:[a-zA-Z\\\\\\_][a-zA-Z0-9\\\\\\_]*))', bygroups(Keyword.Pseudo, Name.Function)),
            (u'(\\\")', bygroups(String), 'expression__2'),
            (u'(\\\')', bygroups(String), 'expression__3'),
            (u'([\\(\\)\\{\\}\\[\\]])', bygroups(Punctuation)),
            (u'(\\$(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\:(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\b\\d+)', bygroups(Number)),
            ('(\n|\r|\r\n)', String),
            (u"(\\])", bygroups(Punctuation), "#pop"),
            ('.', String),
        ], 
        'keyboard_body__2' : [
            (u'(\\{)', bygroups(Punctuation), 'codeblock__1'),
            (u'(@keyboard)', bygroups(Keyword), 'keyboard__1'),
            (u'(@py)([ \\t]*\\{)', bygroups(Keyword, Punctuation), 'expression__1'),
            (u'(=>|<=|>=|==|!=|[=\\*\\|\\+\\-\\/]|>=)', bygroups(Keyword.Pseudo)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*(?=\\())', bygroups(Name.Function)),
            (u'(fun|and|or|not|if|then|else|for|while|in|notin|is|isnot|none|return|ref|expr)(?=[ \\t({}),;+\\-*/])', bygroups(Keyword)),
            (u'(true|false)', bygroups(Number)),
            (u'((?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)\\s+(?=\\=))', bygroups(Number)),
            (u'([\\^\\~]{0,2}[a-gA-GrR](\\\'|,)*[Mm]?([0-9]*)(/[0-9]+)?)', bygroups(Literal)),
            (u'(([vV][0-9]+)|([lL]([0-9]*)(/[0-9]+)?)|([tT][0-9]+)|([sS]([0-9]*)(/[0-9]+)?))', bygroups(Literal)),
            (u'(::)((?:[a-zA-Z\\\\\\_][a-zA-Z0-9\\\\\\_]*))', bygroups(Keyword.Pseudo, Name.Function)),
            (u'(\\\")', bygroups(String), 'expression__2'),
            (u'(\\\')', bygroups(String), 'expression__3'),
            (u'([\\(\\)\\{\\}\\[\\]])', bygroups(Punctuation)),
            (u'(\\$(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\:(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*)(\\\\(?:[a-zA-Z\\_][a-zA-Z0-9\\_]*))*)', bygroups(Name.Variable)),
            (u'(\\b\\d+)', bygroups(Number)),
            ('(\n|\r|\r\n)', String),
            (u"(\\;)", bygroups(Punctuation), "#pop"),
            ('.', String)
        ], 
        'multi_line_comment__1' : [
            ('(\n|\r|\r\n)', String),
            ('.', Comment),
        ], 
        'statement__1' : [
            ('(\n|\r|\r\n)', Generic),
            (u"(\\()", bygroups(Punctuation), "#pop"),
            ('.', Generic)
        ], 
        'statement__2' : [
            ('(\n|\r|\r\n)', Generic),
            ('.', Generic),
        ]
    }

