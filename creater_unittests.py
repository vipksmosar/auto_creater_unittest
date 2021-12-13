import re

class CREATE_UNITTEST_FILE:
    
    def __init__ (self, dict_from_file):
    
        self.dict_from_file = dict_from_file
        
    def __create_file_body(self):
    
        body_string = ''
        for class_name in self.dict_from_file['class_name'].keys():
            class_obj = 'self.test_object'
            class_name_string = 'class Test_{}(TestCase):'.format(class_name)
            class_setup_string = '\n\n\tdef setUp(self):\n\n\t\t{} = {}()\n'.format(class_obj, class_name)
            class_name_string+=class_setup_string
            for method in self.dict_from_file['class_name'][class_name]['methods']:
                if method['def_name'].startswith('__init__'):
                    var = method['def_var'].replace('self,','').replace('self','')
                    if method['test_dict']['in_action']:
                        var = method['test_dict']['in_action']
                    class_name_string = class_name_string.replace('()','({})'.format(var))
                elif not method['def_name'].startswith('_'):
                    var = method['def_var'].replace('self,','').replace('self','')
                    if method['def_return']==0:
                        def_return = ''
                    else:
                        def_return = ': {}'.format(method['def_return'])
                    if method['test_dict']['action']:
                        test_action = method['test_dict']['action']
                        test_action_in = method['test_dict']['in_action']
                        test_action_out = method['test_dict']['out_action']
                        if not var:
                            test_action_in=''
                        method_string = '\n\n\tdef test_{}(self):\n\t\tself.{}({}.{}({}), {})\n\n'.format(method['def_name'], test_action, class_obj ,method['def_name'], test_action_in, test_action_out)
                    else:
                        method_string = '\n\n\tdef test_{}(self):\n\t\tself.asertEqual({}.{}({}), return_value {})\n\n'.format(method['def_name'], class_obj ,method['def_name'], var, def_return)
                    class_name_string+=method_string
            body_string+='{}\n\n'.format(class_name_string)
        
        return body_string
        
    def __create_head(self):
        head_start = 'from unittest import TestCase\n'
        file_name = self.dict_from_file['filename']
        classes_string = ','.join([cls for cls in self.dict_from_file['class_name']])
        return '{}from {} import {}\n\n\n\n'.format(head_start, file_name, classes_string)
        
    def __create_file_content(self):
        head = self.__create_head()
        body = self.__create_file_body()
        tail = '''\nif __name__=="__main__":\n\tuntittest.main()'''
        return '{}{}{}'.format(head,body,tail)
    
    def create_file(self,file_path):
    
        with open(file_path, 'w') as file:
        
            file.write(self.__create_file_content())


class STRING_PATTERN_FINDER:
    
    def __replace_more(self,string):
        return string.replace('\n','').replace(':','').replace('(','').replace(')','').replace('    ','')
    
    def to_find_class(self, string):

        if re.search('^class ', string):
            
            if string.find('#')<string.find('class') and string.find('#')!=-1:
                return 0, 0
            
            elif '(' in string and ')' in string:
                class_name = re.search('\S+\s*[(]', string)[0].replace('(','').replace(')','').replace(' ','')
                parent_class_name = re.search('[(]\S+[)]', string)[0].replace('(','').replace(')','')
                return class_name, parent_class_name

            else:
                class_name = self.__replace_more(re.findall('\S+[:]', string)[0]).replace(' ', '')
                return class_name, 0
            
        else:
            return 0, 0
    
    def to_find_defs(self, string):
        
        if 'def ' in string:
            sub_def = 0
            type_return = 0
            
            if string.find('#')<string.find('def') and string.find('#')!=-1:
                return sub_def, 0, 0, 0
            
            elif re.search(r'\s+def\s+.+:', string):
                if re.search(r'def\s+\S+(.*)\s*->\s*\S+:', string):
                    type_return = re.search('->\s*\S+:',string)[0].replace('->','').replace(' ','').replace(':','')
                sub_def = 1
                def_name = re.search(r'\s+def.+?[(]', string)[0].replace('(','').replace(' def ','').replace(' ','')
                variable_names = re.search(r'[(].+?[)]', string)[0].replace('(','').replace(')','').replace(' ','')
                return sub_def, def_name, variable_names, type_return
            
            elif re.search(r'^def\s+.+:', string):
                if re.search(r'def\s+\S+(.*)\s*->\s*\S+:', string):
                    type_return = re.search('->\s*\S+:',string)[0].replace('->','').replace(' ','').replace(':','')                
                def_name = re.search(r'^def.+?[(]', string)[0][3:].replace('(','').replace(' ','')
                variable_names = re.search(r'[(].*?[)]', string)[0].replace('(','').replace(')','').replace(' ','')
                return sub_def, def_name, variable_names, type_return
            else:
                return 0, 0, 0, 0
        else:
            return 0, 0, 0, 0

    def to_find_qmarks(self, string):
        if "'''" in string or '"""' in string:
            if len(re.findall("'''", string))%2==0 and len(re.findall('"""', string))%2==0:
                return 0
            else:
                return 1
        else:
            return 0    
    
    def to_find_comment(self, string):

        dict_out = {'action':0,'in_action':0,'out_action':0}
        
        if '#' in string:
            index_comment = string.find('#')
            string_comment = string[index_comment+1:]

            if re.search('in\s+(.*)\s+out',string_comment):
                dict_out['in_action'] = re.search('in\s+(.*)\s+out',string_comment)[0]
                dict_out['in_action'] = re.sub('in\s*\(','',dict_out['in_action'])
                dict_out['in_action'] = re.sub('\)\s*out','',dict_out['in_action'])
                
            if re.search('out\s*(.*)\s+end',string_comment):
                dict_out['out_action'] = re.search('out\s*(.*)',string_comment)[0]
                dict_out['out_action'] = re.sub('out\s*\(','', dict_out['out_action'])
                dict_out['out_action'] = re.sub('\)\s+end', '',dict_out['out_action'])

                
            if re.search('is\s+[eq,equal,==,assertequal]+\s+in',string_comment.lower()):
                dict_out['action'] = 'assertEqual'

            return dict_out
            
        else:
            return dict_out
    
    def to_find_import_libs(self, string):
        
        if string.find('import')!=-1:
            
            if string.find('#')<string.find('import') and string.find('#')!=-1:
                return 0, 0
            
            elif re.search('from \S+ import .+', string):
                module = re.search('from \S+ import', string)[0].replace('from','').replace('import', '').replace(' ','')
                object_in_module = re.search('import \S+', string)[0].replace('import', '').replace(' ','')
                return module, object_in_module
            
            elif re.search('import .+', string):
                object_in_module = re.search('import .+', string)[0].replace('import', '').replace(' ','')
                return 0, object_in_module
            else:
                return 0, 0
            
        else:
            return 0,0
            
            
            
class PYTHON_FILE_TO_DICT:
    
    def __init__(self, filename):
    
        self.filename = filename
        self.dict_for_file = {'class_name':{}, 'stand_alone_def_name':[], 'import_libs':[], 'filename':self.filename.replace('.py','')}
    
    def __read_file(self):
        
        with open(self.filename, 'r') as file:
            all_string = file.readlines()
            
        return all_string
    
    def file_to_dict(self):
        class_marker = -1
        qmarks_result = 0
        regex = STRING_PATTERN_FINDER()
        for string in self.__read_file():
            qmarks_result+= regex.to_find_qmarks(string)
            if qmarks_result%2==1:
                continue
            from_s, import_s = regex.to_find_import_libs(string)
            class_name, parent_class_name = regex.to_find_class(string)
            sub_def, def_name, def_variables, def_return = regex.to_find_defs(string)
            dict_comment = regex.to_find_comment(string)
            if import_s:
                self.dict_for_file['import_libs'].append({'from':from_s, 'import':import_s})
                
            elif class_name:
                class_marker=class_name
                self.dict_for_file['class_name'][class_name]={'parent':parent_class_name, 'methods':[]}

            elif sub_def:
                self.dict_for_file['class_name'][class_marker]['methods'].append({'def_name':def_name, 'def_var':def_variables, 'def_return':def_return, 'test_dict':dict_comment})
            
            elif sub_def==0 and def_name!=0:
                class_marker = -1
                self.dict_for_file['stand_alone_def_name'].append({'def_name':def_name, 'variable':def_variables, 'def_return':def_return, 'test_dict':dict_comment})
            
            
        return self.dict_for_file