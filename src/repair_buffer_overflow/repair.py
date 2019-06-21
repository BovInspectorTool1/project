#!/usr/bin/python
#encoding=utf-8
import sys
import getopt
import os
import datetime
import re

API_REP = "API_REP"
FIX_BOUNDARY_CHECK="fix_boundary_check"
INTEGER_CHECK = "integer_check"
MALLOC_CHECK = "malloc_check"
STR_REFORMAT = "str_reformat"
USE_CONCRETE_LEN = "use_concrete_len"
EXTEND = "extend"
LIMIT_INDED_RANGE = "limit_index_range"
STR_END = "str_end"
UNSIGNED_VALUE = "unsigned_value"


#使用模板方法模式
class Method(object):
	tab=''
	def __init__(self,src_code,lineNum,func,mode):
            self.src_code = src_code
	    self.lineNum = lineNum
            self.func = func
	    self.mode = mode

	def instrumentTemplate(self):
            line_Str = self.src_code[self.lineNum-1]
	    #tab=''
	    #print line_Str
	    #tab is the string of \t in front of per line,for alignment
	    for i in line_Str:
                if i == '\t':
                    self.tab+=i
                if i == ' ':
                    self.tab+=i
                else:
                    break
	    #print tab
	    print line_Str
	    line_Str1 = line_Str.strip() #去掉每行头尾空白
	    line_Str2 = line_Str1.replace(' ','')
	    #eg., strcpy(a,b)
	    print self.func
	    print line_Str2
	    if (self.func!="Array bound") and (self.func not in line_Str2):
                print "funcName in report_BFO.txt does not equal to funcName in source code!"
                return None

	    if self.mode == 'default':
                self.src_code.insert(self.lineNum-1,self.tab+'if('+self.repairMethod(self.splitParameters(line_Str2),self.mode)+'){\n'\
                        +self.tab+'\tprintf("'+self.func+' may have a buffer overflow, we just exit\\n");\n'+self.tab+'\treturn 0;\n'+self.tab+'}\n')
	    elif self.mode == API_REP:
                self.src_code[self.lineNum-1] = self.tab+'snprintf('+self.repairMethod(self.splitParameters(line_Str2),self.mode)+');\n'
            elif self.mode == STR_END:
                arrayName = self.splitParameters(line_Str2)[1]
                arraySize = self.findArraySize(arrayName)
                self.src_code.insert(self.lineNum-1,self.tab+'if('+ arrayName + ">" +str(arraySize) +")\n" + self.tab*2 + arrayName + "["+arraySize + "]" + "= '\\0';\n")
            elif self.mode == STR_REFORMAT:
                arg, buf = self.splitParameters(line_Str)
                arg.replace("%s", "%%lds")
                arg.replace("%", "%%")
                template = "{0}char fmt_str[16];\n{1}snprintf (fmt_str, sizeof (fmt_str), {2}, sizeof ({3})-1);\n".format(self.tab, self.tab, arg, buf)
                self.src_code[self.lineNum-1] = self.src_code[self.lineNum-1].replace(arg, "fmt_str")
                self.src_code.insert(self.lineNum-1, template)
            elif self.mode == LIMIT_INDED_RANGE:
                arg = self.splitParameters(line_Str)
                template = "MIN({0}, {1})".format(arg, size)
                size = raw_input("please input the max buffer size.")
                self.src_code[self.lineNum-1] = self.src_code[self.lineNum-1].replace(arg, template)
            elif self.mode == USE_CONCRETE_LEN:
                arg = self.splitParameters(line_Str)
                size = raw_input("please input the specific length.")
                self.src_code[self.lineNum-1] = self.src_code[self.lineNum-1].replace(arg, size)

            return self.src_code

        def findArraySize(self, arrayName):
            size = 0
            for i in range(self.lineNum - 1, 0, -1):
                m = re.search(arrayName+"\[(\d+)\]", self.src_code[i])
                if m and m.group(1):
                    size = m.group(1)
                    break

            return size

	def splitParameters(self,line_Str):
            m = re.search("[if\s\(|while\s\(|for\s\(]?\(*\((.+)\)", line_Str)
            if m and m.group(1):
                info = m.group(1)
                info = info.split(")")[0]

                info = info.split(",")
                return info
            return "NOTFOUND"

	def repairMethod(self,dest_src,mode):
            codition = None
            return condition

class MethodStrcpy(Method):
	#func=''
	def __init__(self,src_code,lineNum,func,mode):
		Method.__init__(self,src_code,lineNum,func,mode)

	def splitParameters(self,line_Str):
		para = line_Str.split(self.func)[1]
		para1 = para.split(')')[0]
		para2 = para1.split('(')[1]
		dest,src = para2.split(',')
		return [dest,src]

	def repairMethod(self,dest_src,mode):
		#Method.repairMethod()
		dest = dest_src[0]
		src = dest_src[1]
		condition=''
		if self.mode == 'default':
			condition = 'strlen('+src+') >= sizeof('+dest+')'
		if self.mode == API_REP:
			condition = dest+',sizeof('+dest+'),\"%s\",'+src
		return condition

class MethodStrncpy(Method):
	#eg., strncpy(a,b,n)
	def __init__(self,src_code,lineNum,func,mode):
		Method.__init__(self,src_code,lineNum,func,mode)

	def splitParameters(self,line_Str):
		para = line_Str2.split(func)[1]
		para1 = para.split(')')[0]
		para2 = para1.split('(')[1]
		dest,src,n = para2.split(',')
		return [dest,n]

	def repairMethod(self,dest_src,mode):
		#Method.repairMethod()
		dest = dest_src[0]
		n = dest_src[1]
		condition = n+' > sizeof('+dest+')'
		return condition

class MethodStrcat(Method):
	#func=''
	#eg., strcat(a,b)
	def __init__(self,src_code,lineNum,func,mode):
		Method.__init__(self,src_code,lineNum,func,mode)

	def splitParameters(self,line_Str):
		para = line_Str.split(self.func)[1]
		para1 = para.split(')')[0]
		para2 = para1.split('(')[1]
		dest,src = para2.split(',')
		return [dest,src]

	def repairMethod(self,dest_src,mode):
		#Method.repairMethod()
		dest = dest_src[0]
		src = dest_src[1]
		condition=''
		if self.mode == 'default':
			condition = 'strlen('+src+')+strlen('+dest+') >= sizeof('+dest+')'
		if self.mode == API-REP:
			condition = dest+'+strlen('+dest+'),sizeof('+dest+')-strlen('+dest+'),\"%s\",'+src
		return condition

class MethodStrncat(Method):
	#eg., strncat(a,b,n)
	def __init__(self,src_code,lineNum,func,mode):
		Method.__init__(self,src_code,lineNum,func,mode)

	def splitParameters(self,line_Str):
		para = line_Str.split(self.func)[1]
		para1 = para.split(')')[0]
		para2 = para1.split('(')[1]
		dest,src,n = para2.split(',')
		return [dest,src,n]

	def repairMethod(self,dest_src,mode):
		#Method.repairMethod()
		dest = dest_src[0]
		src = dest_src[1]
		n = dest_src[2]
		condition = '(strlen('+src+')<='+n+' ? strlen('+src+') : '+n+')+strlen('+dest+') >= sizeof('+dest+')'
		return condition

class MethodSscanf(Method):
    #eg., int sprintf ( char * str, const char * format, ... );
    def __init__(self,src_code,lineNum,func,mode):
        Method.__init__(self,src_code,lineNum,func,mode)

    def splitParameters(self,line_Str):
        if self.mode == STR_REFORMAT:
            data = super(MethodSscanf, self).splitParameters(line_Str)
            return data[1].strip(), data[-1].strip()

    def repairMethod(self,dest_src,mode):
        #Method.repairMethod()
        dest = dest_src[0]
        formatStr = dest_src[1]
        if mode == STR_REFORMAT:
            condition = None
        return condition

class MethodSprintf(Method):
    #eg., int sprintf ( char * str, const char * format, ... );
    def __init__(self,src_code,lineNum,func,mode):
        Method.__init__(self,src_code,lineNum,func,mode)

    def splitParameters(self,line_Str):
        para = line_Str.split(self.func)[1]
        para1 = para.split(')')[0]
        para2 = para1.split('(')[1]
        dest,formatStr = para2.split(',',1)
        if self.mode == STR_END:
            #return dest, arrayName
            return [dest, formatStr.split(",")[-1]]
        return [dest,formatStr]

    def repairMethod(self,dest_src,mode):
        #Method.repairMethod()
        dest = dest_src[0]
        formatStr = dest_src[1]
        if mode == 'default':
            self.src_code.insert(self.lineNum-1,tab+'#include "MY_vsnprintf.h"\n')
            condition = '(MY_vsnprintf('+formatStr+') >= sizeof('+dest+')'
        elif mode == API-REP:
            condition = dest+',sizeof('+dest+'),'+formatStr
        elif mode == STR_END:
            self.src_code.insert(self.lineNum-1, )
        return condition

class MethodSnprintf(Method):
	#eg., int snprintf ( char * s, size_t n, const char * format, ... );
	def __init__(self,src_code,lineNum,func,mode):
		Method.__init__(self,src_code,lineNum,func,mode)

	def splitParameters(self,line_Str):
		para = line_Str.split(self.func)[1]
		para1 = para.split(')')[0]
		para2 = para1.split('(')[1]
		dest,n = para2.split(',',2)[0:2]
		return [dest,n]

	def repairMethod(self,dest_src,mode):
		#Method.repairMethod()
		dest = dest_src[0]
		n = dest_src[1]
		condition = n+' > sizeof('+dest+')'
		return condition

class MethodRead(Method):
	#eg., ssize_t read(int fd, void *buf, size_t count);
	#count > size(buf)
	def __init__(self,src_code,lineNum,func,mode):
		Method.__init__(self,src_code,lineNum,func,mode)

	def splitParameters(self,line_Str):
		para = line_Str.split(self.func)[1]
		para1 = para.split(')')[0]
		para2 = para1.split('(')[1]
		fd,dest,count = para2.split(',')
		return [dest,count]

	def repairMethod(self,dest_src,mode):
		#Method.repairMethod()
		dest = dest_src[0]
		count = dest_src[1]
		condition = count+' > sizeof('+dest+')'
		return condition

class MethodFread(Method):
	#eg., size_t fread ( void * ptr, size_t size, size_t count, FILE * stream );
	#size*count > size(ptr)
	def __init__(self,src_code,lineNum,func,mode):
		Method.__init__(self,src_code,lineNum,func,mode)

	def splitParameters(self,line_Str):
		para = line_Str.split(self.func)[1]
		para1 = para.split(')')[0]
		para2 = para1.split('(')[1]
		dest,size,count,stream = para2.split(',')
		return [dest,size,count]

	def repairMethod(self,dest_src,mode):
		#Method.repairMethod()
		dest = dest_src[0]
		size = dest_src[1]
		count = dest_src[2]
		condition = size*count+' > sizeof('+dest+')'
		return condition

class MethodFgets(Method):
	#eg., char * fgets ( char * str, int num, FILE * stream );
	#num > size(str)
	def __init__(self,src_code,lineNum,func,mode):
		Method.__init__(self,src_code,lineNum,func,mode)

	def splitParameters(self,line_Str):
		para = line_Str.split(self.func)[1]
		para1 = para.split(')')[0]
		para2 = para1.split('(')[1]
		dest,n,stream = para2.split(',')
		return [dest,n]

	def repairMethod(self,dest_src,mode):
		#Method.repairMethod()
		dest = dest_src[0]
		n = dest_src[1]
		condition = n+' > sizeof('+dest+')'
		return condition

class MethodArrayBound(Method):
	#eg., buf[i]=x
	#eg., *(buf+i)=x
	def __init__(self,src_code,lineNum,func,mode):
		Method.__init__(self,src_code,lineNum,func,mode)

	def splitParameters(self,line_Str):
		if '[' in line_Str:
			#eg., buf[i]=x
			arrayName,para0 = line_Str.split('[')
			index0 = para0.split(']')[0]
			return [arrayName,index0]
		elif '*' in line_Str2 and '(' in line_Str2 and '+' in line_Str2:
			#eg., *(buf+i)=x
			para0,para1 = line_Str.split('+')
			arrayName = para0.split('(')[1]
			index0 = para1.split(')')[0]
			return [arrayName,index0]
		else:
			print "cannot match code pattern!"
			return None

	def repairMethod(self,dest_src,mode):
		#Method.repairMethod()
		arrayName = dest_src[0]
		index0 = dest_src[1]
		condition = index0+'*sizeof('+arrayName+'[0]) >= sizeof('+arrayName+')'
		return condition

class OtherMethod(Method):
    #eg., buf[i]=x
    #eg., *(buf+i)=x
    def __init__(self,src_code,lineNum,func,mode):
        Method.__init__(self,src_code,lineNum,func,mode)

    def instrumentTemplate(self):
        line_Str = self.src_code[self.lineNum-1]
        #tab=''
        #print line_Str
        #tab is the string of \t in front of per line,for alignment
        for i in line_Str:
            if i == '\t':
                self.tab+=i
                if i == ' ':
                    self.tab+=i
                else:
                    break
        #print tab
        print line_Str
        line_Str1 = line_Str.strip() #去掉每行头尾空白
        line_Str2 = line_Str1.replace(' ','')
        #eg., strcpy(a,b)
        print self.func
        print line_Str2

        if self.mode == FIX_BOUNDARY_CHECK:
            self.src_code[self.lineNum-1] = line_Str.replace("<", "<=")
            self.src_code[self.lineNum-1] = self.src_code[self.lineNum-1].replace(">", ">=")
            return self.src_code
        elif self.mode == INTEGER_CHECK:
            midBraBeg = line_Str.find("(")
            if midBraBeg != -1:
                p1 = line_Str.find(")", midBraBeg + 1)
                p2 = line_Str.find(",", midBraBeg + 1)
                if p1 == -1:
                    midBraEnd = p2
                elif p2 == -1:
                    midBraEnd = p1
                else:
                    midBraEnd = min(p1, p2)
            arrayBraBeg = line_Str.find("[")
            if arrayBraBeg != -1:
                arrayBraEnd = line_Str.rfind("]")

            if arrayBraBeg == -1:
                intText = line_Str[midBraBeg+1: midBraEnd]
            elif midBraBeg == -1:
                intText = line_Str[arrayBraBeg+1: arrayBraEnd]
            else:
                intText = line_Str[arrayBraBeg+1: arrayBraEnd]
            whiteSpaceLen = len(line_Str) - len(line_Str.lstrip())
            firstState = " "*whiteSpaceLen+"if("+intText+"<"+intText.split("+")[0]+")\n"
            secondState = " "*(whiteSpaceLen + 4) + "return 0;\n"
            self.src_code[self.lineNum-1] = firstState + secondState + line_Str
            return self.src_code
        elif self.mode == MALLOC_CHECK:
            splitVar = line_Str.split("=")[0].split(" ")
            varName = "UNKNOWN"
            for i in range(len(splitVar) - 1, 0, -1):
                if splitVar[i] != "":
                    varName = splitVar[i]
                    break
            whiteSpaceLen = len(line_Str) - len(line_Str.lstrip())
            firstState = " "*whiteSpaceLen+"if("+varName+")\n"
            secondState = " "*(whiteSpaceLen + 4) + "return 0;\n"
            self.src_code[self.lineNum-1] = line_Str + firstState + secondState
            return self.src_code
        elif self.mode == UNSIGNED_VALUE:
            whiteSpaceLen = len(line_Str) - len(line_Str.lstrip())
            line_Str = line_Str[:whiteSpaceLen] + "unsigned " + line_Str[whiteSpaceLen:]
            self.src_code[self.lineNum-1] = line_Str
            return self.src_code
        elif self.mode == LIMIT_INDED_RANGE:
            data = super(OtherMethod, self).splitParameters(line_Str)
            ind = input("please input the arg index.")
            size = raw_input("please input the max buffer size.")
            arg = data[ind].strip()
            template = "MIN({0}, {1})".format(arg, size)
            self.src_code[self.lineNum-1] = self.src_code[self.lineNum-1].replace(arg, template)
            return self.src_code
        elif self.mode == EXTEND:
            m = re.search("\[(\d+)\]", line_Str)
            if m and m.group(1):
                data = m.group(1)
            self.src_code[self.lineNum-1] = self.src_code[self.lineNum-1].replace(data, str(int(data)*2))
            return self.src_code


        def splitParameters(self,line_Str):
            return

        def repairMethod(self,dest_src,mode):
            return 0



class MethodMemcpy(Method):
    #eg., buf[i]=x
    #eg., *(buf+i)=x
    def __init__(self,src_code,lineNum,func,mode):
        Method.__init__(self,src_code,lineNum,func,mode)


    def splitParameters(self,line_Str):
        if self.mode == LIMIT_INDED_RANGE:
            data = super(MethodMemcpy, self).splitParameters(line_Str)
            return data[2].strip()
        elif self.mode == USE_CONCRETE_LEN:
            data = super(MethodMemcpy, self).splitParameters(line_Str)
            return data[2].strip()
        return None

    def repairMethod(self,dest_src,mode):
        return 0



#使用工厂模式
class FuncRepairMethodFactory:
	#def __init__(self):
	function = {'strcpy':MethodStrcpy,'strncpy':MethodStrncpy,'strcat':MethodStrcat,\
	'strncat':MethodStrncat,'sprintf':MethodSprintf,'snprintf':MethodSnprintf,\
	'read':MethodRead,'fread':MethodFread,'fgets':MethodFgets,'Array bound':MethodArrayBound, \
        'sscanf':MethodSscanf, 'memcpy':MethodMemcpy}

        def repairIfUniversal(self, mode):
            if mode == FIX_BOUNDARY_CHECK:
                return True
            elif mode == INTEGER_CHECK:
                return True
            elif mode == MALLOC_CHECK:
                return True
            elif mode == UNSIGNED_VALUE:
                return True
            elif mode == LIMIT_INDED_RANGE:
                return True
            elif mode == USE_CONCRETE_LEN:
                return False
            elif mode == STR_END:
                return False
            elif mode == STR_REFORMAT:
                return False

        def createMethod(self,src_code,lineNum,func,mode):
            if self.repairIfUniversal(mode):
                method = OtherMethod(src_code,lineNum,func,mode)
            if self.function.get(func) != None:
                method = self.function.get(func)(src_code,lineNum,func,mode)
            else:
                method = OtherMethod(src_code,lineNum,func,mode)
            return method
#使用单例模式
class Singleton(object):
	def __new__(cls, *args, **kw):
		#如果cls._instance为None说明该类还没有实例化过,实例化该类,并返回
		#如果cls._instance不为None,直接返回cls._instance
		if not hasattr(cls, '_instance'):
			orig = super(Singleton, cls)
			cls._instance = orig.__new__(cls, *args, **kw)
		return cls._instance

class Repair(Singleton):
	BFO_position = []

	def __init__(self,mode,reportFile):
		self.mode = mode
		self.workingDir = os.path.dirname(reportFile) + "/"
		self.BFO_position = read_report_BFO_txt(reportFile)


	def repair(self):
		fac = FuncRepairMethodFactory()

		if self.BFO_position == None:
			return 0
		fileLine={}
		#fileLine eg., {'src.c': ['12', '11']}
		file_line_func={}
		#file_line_func eg., {'src_12': 'strcpy'}

		for BFO_position_i in self.BFO_position:
			#eg., src.c_12 strcat
			#eg., src.c_8 Array bound
			file_line,func = BFO_position_i.split('\n')[0].split(' ',1)
			file_line_func[file_line] = [func]
			tmpData = file_line.split('_')
                        fileName = '_'.join(tmpData[:-1])
                        line = tmpData[-1]
			if fileLine.get(fileName) == None:
				fileLine[fileName] = [int(line)]
			else:
				fileLine[fileName].append(int(line))
		#print fileLine
		print file_line_func

		for key in fileLine.keys():
			#print fileLine[key]
			#倒序插装
			#eg., we first instrument line 14,then instrument line 12,in case of after instrument,
			#the line NUM after that instrument will change
			fileLine[key].sort(reverse=True)
			#print fileLine[key]
		print fileLine

		for key in fileLine.keys():
			f = open(self.workingDir+key)
			src_code = f.readlines()
			f.close()
			for line in fileLine[key]:
				funcName = file_line_func[key+'_'+str(line)][0]
				funcMethod = fac.createMethod(src_code,line,funcName,self.mode)
				src_code = funcMethod.instrumentTemplate()
				if src_code == None:
					return 0
			f2 = open(key+"_repaired",'w')
			f2.writelines(src_code)
			f2.close()
		return 1

def read_report_BFO_txt(reportFile):
	#contents: src.c_12 strcpy\n
	if os.path.exists(reportFile)==False:
		print "report_BFO.txt doesn't exist"
		return None
	f = open(reportFile)
	try:
		lines = f.readlines()
		print lines
	finally:
		f.close()
	return lines

def Usage():
	print 'buffer overflow repair instrument.py usage:'
	print 'python thisfile.py -m mode src.c report.txt'
	print 'Input file needed: src.c,report_BFO.txt'
	print 'Output file: src.c(repaired)'
	print '-h,--help: print help message.'
	print '-m,--mode: choose the mode you use to repair your C/C++ source files,'
	print '\t default: add bounds checking'
	print '\t API_REP: replace API with strncpy/snprintf'
	print '\t extend: extend the array to avoid buffer overflow'
	print '\t fix_boundary_check: modify boundary check'
	return 0

def main(argv):
	try:
		opts, args = getopt.getopt(argv[1:],'hm:',['help','mode='])
	except getopt.GetoptError, err:
		print str(err)
		Usage()
		sys.exit(2)
	if opts == []:
		starttime = datetime.datetime.now()
		repairObject = Repair('default', args[0])
		res = repairObject.repair()
		if res == 0:
			print "An error occured when instrument!"
		endtime = datetime.datetime.now()
		print (endtime - starttime).seconds
		sys.exit(0)
	for o,a in opts:
		if o in('-h','--help'):
			Usage()
			sys.exit(1)
		elif o in('-m','--mode'):
			starttime = datetime.datetime.now()
			print "a: ",a
			repairObject = Repair(a, args[0])
			res = repairObject.repair()
			if res == 0:
				print "An error occured when instrument!"
			endtime = datetime.datetime.now()
			print (endtime - starttime).seconds
			sys.exit(0)
		else:
			print 'unhandled option'
			sys.exit(3)

	#return 0

if __name__ == "__main__":
    main(sys.argv)
