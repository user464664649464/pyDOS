






import json, os, sys

class DOSException:
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class DOSWarning:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class DOSFilenameError(DOSException):
    def __init__(self, msg = "Invalid filename or directory name"):
        super().__init__(f"{msg}")


class DOSFileNotFoundError(DOSException):
    def __init__(self, NotFoundPath = "", msg = "is not found"):
        super().__init__(f"{NotFoundPath} {msg}")

class DosCannotDeleteParentError(DOSException):
    def __init__(self, msg = "Cannot delete parent directory"):
        super().__init__(f"{msg}")

class Directory:
    def __init__(self, name, parent = None):
        self.name = name
        self.children =[]
        self.parent = parent
    
    @property
    def childrenNames(self):
        return [i.name for i in self.children]
    
    def add(self, name, isDirectory):
        child = Directory(name, parent = self) if isDirectory else File(name)
        ls1 = self.childrenNames
        st1 = set(ls1[:])
        if len(st1) != len(ls1): return DOSFilenameError()
        if isDirectory:
            errChars = [x in child.name for x in ['/', '\'','"', '.']]
            if any(errChars): return DOSFilenameError()
        self.children.append(child)
    
    def addChild(self, child):
        child.parent = self
        self.children.append(child)
   
    def dir(self):
        print(eval(f"\"%-{os.get_terminal_size().columns//2}s%{os.get_terminal_size().columns//2}s\"%(\"name\", \"type\")"))
        print("-"*os.get_terminal_size().columns)
        print(eval(f"\"%-{os.get_terminal_size().columns//2}s%{os.get_terminal_size().columns//2}s\"%(\".\", \"Directory\")"))
        if self.parent:
            print(eval(f"\"%-{os.get_terminal_size().columns//2}s%{os.get_terminal_size().columns//2}s\"%(\"..\", \"Directory\")"))
        for i in self.children:
            print(eval(f"\"%-{os.get_terminal_size().columns//2}s%{os.get_terminal_size().columns//2}s\"%(i.name, type(i).__name__)"))
    
    def copy(self):
        f = Directory(self.name, self.parent)
        for i in self.children:
            f.addChild(i.copy())
        return f

    def chdir(self, path):
        if path == "": return self
        if path == "..": return self.parent if self.parent else DOSFileNotFoundError(self.name, "does not have a parent directory")
        
        elif path == ".": return self
        path = path.split("/")
        if len(path) == 1:
            if path[0] in [i.name for  i in self.children]: return sorted(self.children, key = lambda x: int(x.name == path[0]))[-1]
            else: return DOSFileNotFoundError(path[0])
        else:
            if path[0] in [i.name for i in self.children]:
                return sorted(self.children, key = lambda x: int(x.name == path[0]))[-1].foundPath("/".join(path[1:]), self)
            else: return DOSFileNotFoundError("/".join(path))

    def delete(self, path):
        if path == "": return 
        
        if path == "..":
            DosCannotDeleteParentError()
        else:
            path = path.split("/")
            if path[-1] == "*":
                path = path[:-1]
                parentDir = self.chdir("/".join(path))
                parentDir.children = []
            else:
                path = path[:-1] if len(path) > 1 else path
                parentDir = self.chdir("/".join(path)) if len(path) > 1 else self
                parentDir.children.remove(self.chdir(path[-1])) if not isinstance(self.chdir(path[-1]), DOSException) else print(parentDir)
        
    def getString(self):
        return f"Directory(name = {self.name}, children = {[i.getString() for i in self.children]})"
    
    def __str__(self):
        return self.getString()

    def foundPath(self):
        return (self.parent.foundPath() + "/" + self.name) if self.parent else self.name
        

class File:
    def __init__(self, name, data = "", byte = False, parent = None):
        self.name = name
        self.data = data
        self.parent = parent
        self.byte = byte
        self.update()
    
    def update(self):
        if self.byte:
            self.data = bytes(self.data.encode("utf-8"))
        
    def add(self, data):
        self.data += bytes(data.encode("utf-8")) if self.byte else str(data)
    
    def write(self, data):
        self.data = data.replace("<\\br>", "\n")
    
    def clear(self):
        self.data = ""

    def read(self):
        return self.data
    
    def copy(self):
        f = File(self.name, self.data, self.byte, self.parent)
        return f
    
    def run(self):
        exec(self.data)
    
    def getString(self):
        return f"File(name = {self.name}, data = {self.data}, is_byte = {self.byte})"
    
    def __str__(self):
        return self.getString()




class CommandWindow:
    def __init__(self, fileObj):
        self.fileObj = fileObj
        self.files = json.load(self.fileObj)
        self.files = self.create(self.files)
        self.updateFiles()
        
    
    def updateFiles(self):
        self.COMMAND_FUNC = {
            "dls": self.files.dir, 
            "cd": self.files.chdir,
            "nfd": self.files.add,
            "cls": lambda: os.system("cls"),
            "exit": self.exit,
            "del": self.files.delete,
            "read": lambda path: print(self.files.chdir(path).read()),
            "run": lambda path: self.files.chdir(path).run(),
            "write": lambda path, data: self.files.chdir(path).write(data),
            "echo": self.echo,
            "import": self.importF,
            "export": self.exportF,
            "help": lambda: print("""
                                命令列表:
                                dls - 列出当前目录的所有文件和目录。
                                cd - 更改当前目录。
                                    用法：cd <目录名称>。
                                nfd - 创建新文件或目录。
                                    用法：nfd <文件名> <是否为文件>。
                                    注：如果是文件，则在<是否为文件>选项内随便输入字符，若为文件夹，须留空。
                                    但是，文件夹的名称不能包含以下字符：/ \\ " . 空格
                                    例如：nfd test.txt 1
                                    nfd test 
                                            ^这里一定一定要有空格
                                    
                                cls - 清除命令窗口。
                                exit - 退出命令窗口。
                                del - 删除文件或目录。
                                    用法：del <文件名>。
                                read - 读取文件内容。
                                    用法：read <文件名>。
                                run - 运行文件。
                                    用法：run <文件名>。
                                write - 写入文件内容。
                                    用法：write <文件名> <文件内容>。
                                echo - 输出文本。
                                    用法：echo <文本>。
                                help - 显示命令列表。""")
        }
    
    def create(self, files):
        Object = None
        if files['type'] == 'directory':
            Object = Directory(files['name'])
            for i in files['children']:
                warn = Object.addChild(self.create(i))
                if isinstance(warn, DOSWarning | DOSException): print("DOSWarning: ", warn)
        elif files['type'] == 'file':
            Object = File(files['name'], files['data'], files['byte'])
        return Object

    def importF(self, path, byte = False):
        if not os.path.exists(path): return DOSFileNotFoundError(path)
        with open(path, "r") as f:
            fileName = os.path.basename(path)
            data = f.read()
            self.files.add(fileName, 0)
            file = self.files.chdir(fileName)
            file.byte = byte
            file.write(data)
            file.update()

    def exportF(self, fileName):
        llExport = self.files.chdir(fileName)
        if isinstance(llExport, DOSException): return llExport
        with open(fileName, "w", encoding="utf-8") as f:
            f.write(llExport.data)
    
    def save(self, FileObj):
        f = dict()
        if type(FileObj) == Directory:
            f.update({
                'name': FileObj.name,
                'type': 'directory',
                'children': [self.save(i) for i in FileObj.children]
            })
        elif type(FileObj) == File:
            f.update({
                'name': FileObj.name,
                'type': 'file',
                'data': FileObj.data,
                'byte': FileObj.byte  
            })
        return f
    
    def echo(self, *args):
        print(*args)

    def main(self):
        while True:
            try:
                command = input(self.files.foundPath() + ">").split(" ")
                if command[0] in self.COMMAND_FUNC:
                    if command[0] == "cd": self.files = self.COMMAND_FUNC[command[0]](*command[1:]) if isinstance(errorMsg:=self.COMMAND_FUNC[command[0]](*command[1:]), Directory) else self.files;print(errorMsg) if isinstance(errorMsg, DOSException) else None
                    elif command[0] == "nfd": self.files.add(*command[1:])
                    elif command[0] == "write": self.COMMAND_FUNC["write"](command[1]," ".join(command[2:]))
                    else: self.COMMAND_FUNC[command[0]](*command[1:])
                else: print(f"{command[0]} 不是有效的命令。")
            except KeyboardInterrupt:
                self.exit()
            except Exception as e:
                print(e)
            self.updateFiles()
    def exit(self):
        while True:
            if self.files.parent:
                self.files = self.files.parent
            else:
                break
        filesTemp = self.files.copy()
        fo=open("files.json","w")
        json.dump(self.save(filesTemp), fo)
        fo.close()
        self.fileObj.close()
        sys.exit()

def main():
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    with open("files.json","r") as f:
        cmd = CommandWindow(f)
        cmd.main()