import re

class CREATE_UNITTEST_FILE:
    
    def __init__ (self, dict_from_file):
    
        self.dict_from_file = dict_from_file
        
    def __create_file_body(self):
    
        body_string = ''
        for class_name in self.dict_from_file['class_name'].keys():
            class_obj = 'self.test_object'
            class_name_string = 'class Test_{}(unittest.TestCase):'.format(class_name)
            class_setup_string = '\n\n\tdef setUP(self):\n\n\t\t{} = {}()\n\n'.format(class_obj, class_name)
            class_name_string+=class_setup_string
            for method in self.dict_from_file['class_name'][class_name]['methods']:
                if not method['def_name'].startswith('_'):
                    var = method['def_var'].replace('self,','').replace('self','')
                    method_string = '\n\n\tdef test_{}(self):\n\t\t{}.{}({})\n\t\tpass\n'.format(method['def_name'], class_obj ,method['def_name'], var)
                    class_name_string+=method_string
            body_string+='{}\n\n'.format(class_name_string)
        
        return body_string
        
    def __create_file_content(self):
    
        head = 'import unittest\n\n\n\n'
        body = self.__create_file_body()
        tail = '''\nif __name__==__main__:\n\tuntittest.main()'''
        return '{}{}{}'.format(head,body,tail)
    
    def create_file(self,file_path):
    
        with open(file_path, 'w') as file:
        
            file.write(self.__create_file_content())


class STRING_PATTERN_FINDER:
    
    def __replace_more(self,string):
        return string.replace('\n','').replace(':','').replace('(','').replace(')','').replace('    ','')
    
    def to_find_class(self, string):

        if 'class ' in string:
            
            if string.find('#')<string.find('class') and string.find('#')!=-1:
                return 0, 0
            
            elif '(' in string and ')' in string:
                class_name = re.findall('\S+[(]', string)[0].replace('(','').replace(')','')
                parent_class_name = re.findall('[(]\S+[)]', string)[0].replace('(','').replace(')','')
                return class_name, parent_class_name

            else:
                class_name = self.__replace_more(re.findall('\S+[:]', string)[0]).replace(' ', '')
                return class_name, 0
            
        else:
            return 0, 0
    
    def to_find_defs(self, string):
        
        if 'def ' in string:
            sub_def = 0
            
            if string.find('#')<string.find('def') and string.find('#')!=-1:
                return sub_def, 0, 0
            
            elif re.search(r'\s+def\s+.+:', string):
                sub_def = 1
                def_name = re.search(r'\s+def.+?[(]', string)[0].replace('(','').replace('def','').replace(' ','')
                variable_names = re.search(r'[(].+?[)]', string)[0].replace('(','').replace(')','').replace(' ','')
                return sub_def, def_name, variable_names
            
            elif re.search(r'^def\s+.+:', string):
                def_name = re.search(r'^def.+?[(]', string)[0].replace('(','').replace('def','').replace(' ','')
                variable_names = re.search(r'[(].*?[)]', string)[0].replace('(','').replace(')','').replace(' ','')
                return sub_def, def_name, variable_names
            
        else:
            return 0, 0, 0
    
    
    def to_find_comment(self, string):
        pass
    
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
            return 0,0
            
            
            
class PYTHON_FILE_TO_DICT:
    
    def __init__(self, filename):
    
        self.filename = filename
        self.dict_for_file = {'class_name':{}, 'stand_alone_def_name':[], 'import_libs':[]}
    
    def __read_file(self):
        
        with open(self.filename, 'r') as file:
            all_string = file.readlines()
            
        return all_string
    
    def file_to_dict(self):
        class_marker = -1
        regex = STRING_PATTERN_FINDER()
        for string in self.__read_file():
        
            from_s, import_s = regex.to_find_import_libs(string)
            class_name, parent_class_name = regex.to_find_class(string)
            sub_def, def_name, def_variables = regex.to_find_defs(string)
            
            if import_s:
                self.dict_for_file['import_libs'].append({'from':from_s, 'import':import_s})
                
            elif class_name:
                class_marker=class_name
                self.dict_for_file['class_name'][class_name]={'parent':parent_class_name, 'methods':[]}

            elif sub_def:
                self.dict_for_file['class_name'][class_marker]['methods'].append({'def_name':def_name, 'def_var':def_variables})
            
            elif sub_def==0 and def_name!=0:
                class_marker = -1
                self.dict_for_file['stand_alone_def_name'].append({'def_name':def_name, 'variable':def_variables})
            
            
        return self.dict_for_file