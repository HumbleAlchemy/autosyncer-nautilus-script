# ==================================================
# @author   : Abhishek Nair
# @desc     : This script add menu options to nautilus menu using nautilus-python 
#             library. It generates menu options from a json file and writes the 
#             data corresponding to menu select events to another json which is used
#             by our autosync script for syncing.         
# ================================================== 

import os
import json
import logging
from gi.repository import Nautilus, GObject

class ColumnExtension(GObject.GObject, Nautilus.MenuProvider):
    

    # ================= LOGGING ===================== 
    # create logger
    lgr = logging.getLogger('autosyncer')
    lgr.setLevel(logging.DEBUG)
    # add a file handler
    LOG_FILE = ".config/autosyncer/app.log"
    fh = logging.FileHandler(os.path.join(os.environ['HOME'],LOG_FILE))
    fh.setLevel(logging.DEBUG)
    # create a formatter and set the formatter for the handler.
    format = '%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s'
    # frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    frmt = logging.Formatter(format)
    
    fh.setFormatter(frmt)
    # add the Handler to the logger
    lgr.addHandler(fh)
    # ================= LOGGING ===================== 

    
    # data file holds data of files and folders
    DATA_FILE = ".config/autosyncer/data.json"
    DATA_FILE_PATH = os.path.join(os.environ['HOME'],DATA_FILE)

    # config file holds data about user's clouds
    CLOUD_FILE = ".config/autosyncer/clouds.json"
    CLOUD_FILE_PATH = os.path.join(os.environ['HOME'],CLOUD_FILE)

    # 
    def __init__(self):
        pass

    # load json clouds file
    def __import_clouds(self):
        json_file = open(self.CLOUD_FILE_PATH,"r")
        clouds = json.load(json_file)
        json_file.close()
        return clouds


    # load json data file
    def __import_data(self):

        # if file has no data write empty data
        print os.stat(self.DATA_FILE_PATH).st_size
        if(os.stat(self.DATA_FILE_PATH).st_size == 0):
            init_json = { "folders" : [] , "files" : [] }
            self.__export_data(init_json)
            print "initialized file"

        json_file = open(self.DATA_FILE_PATH,"r")
        data = json.load(json_file)
        json_file.close()
        return data

    # copy json data back to json file
    def __export_data(self,data):
        json_file = open(self.DATA_FILE_PATH,"w")
        json_file.write(json.dumps(data))
        json_file.close()


    # add file to JSON config file
    def add_file(self,file_name,parent_folder_path , cloud):
        data = self.__import_data()
        file_full_path = parent_folder_path + "/" + file_name

        result = os.system("java -jar AddFileToAutosync.jar " + cloud["name"] + " " + str(cloud["user_cloudID"]) + " " + file_full_path)
        
        if(result == 0 ):
            # creating new dictionary element
            new_file_data = { "file" : file_name , "parent" : parent_folder_path , "name" : cloud["name"] , "user_cloud_name" : cloud["user_cloud_name"] , "user_cloudID" : cloud["user_cloudID"]}
        
            # adding new file to data object
            data["files"].append(new_file_data)

            # exporting data
            self.__export_data(data)
        


    # remove file to JSON config file
    def remove_file(self,file_name,parent_folder_path):
        data = self.__import_data()

        files = data["files"]
        # create dictionary element to match
        file_data = { "file" : file_name , "parent" : parent_folder_path }
        
        for e in files:
            if(e["file"] == file_data["file"] and e["parent"] == file_data["parent"]):
                files.remove(e)
                self.lgr.debug("removed: " + str(e) + " and matched: " + str(file_data))

        # exporting data
        self.__export_data(data)

    # add folder to JSON config file
    def add_folder(self,folder_path , cloud):
        data = self.__import_data()
        
        # Upload directory to cloud initially
        result = os.system("java -jar AddToAutosync.jar " + cloud["name"] + " " + str(cloud["user_cloudID"]) + " " + folder_path)
        # result = 0
        # self.lgr.debug("result of folder add: " + str(result))
        
        
        if(result == 0 ):
            # creating new dictionary element
        	new_folder_data = { 
        		"folder" : folder_path , 
        		"name" : cloud["name"] , 
        		"user_cloud_name" : cloud["user_cloud_name"] , 
        		"user_cloudID" : cloud["user_cloudID"] }
	
        	# addind new folder to data object
        	data["folders"].append(new_folder_data)

        	# exporting data 
        	self.__export_data(data)
        
        	# self.lgr.debug("result on error: " + str(result))

    # remove folder to JSON config file
    def remove_folder(self,folder_path):
        data = self.__import_data()

        # in python only the reference is copied so changes made to folders will
        # reflect in data, I think this is because a list is immutable type
        folders = data["folders"]

        # creating new dictionary element
        folder_data = { "folder" : folder_path }

        # remove selected folder from data object
        for e in folders:
            if(e["folder"] == folder_data["folder"]):
                folders.remove(e)
                self.lgr.debug("removed: " + str(e["folder"]) + " and matched: " + str(folder_data["folder"]))

        # exporting data 
        self.__export_data(data)

    # check if file or folder already exists
    def exists(self,file):
        data = self.__import_data()
        if(file.is_directory()):
            folder_data = { "folder" : file.get_location().get_path() }
            for i in data["folders"]:
                if(i["folder"] == folder_data["folder"]):
                    return True
            return False
        else:

            file_data = { "file" : file.get_name() , "parent" : file.get_parent_location().get_path() }
            for i in data["files"]:
                if(i["file"] == file_data["file"] and i["parent"] == file_data["parent"]):
                    return True
            return False

    def menu_activate_cb(self, menu, file , cloud):
        # print "menu_activate_cb",file
        # os.system("gedit " + file.get_name())
        if (file.is_directory()):
            self.add_folder(file.get_location().get_path() , cloud)
        else:
            self.add_file(file.get_name(),file.get_parent_location().get_path() , cloud)

    def menu_deactivate_cb(self,menu,file):
        #remove file or folder from data.json
        if (file.is_directory()):
            self.remove_folder(file.get_location().get_path())
        else:
            self.remove_file(file.get_name(),file.get_parent_location().get_path())

    def get_file_items(self, window, files):
        if len(files) != 1:
            return
        
        file = files[0]

        # check if entry already exists
        # if it does show another menu option that removes it from data.json file
        if(self.exists(file)):
            item = Nautilus.MenuItem(
                name="SimpleMenuExtension::Menu",
                label="Remove from Kumo",
                tip="Remove"
            )
            
            item.connect('activate', self.menu_deactivate_cb, file)
        else:

            item = Nautilus.MenuItem(
                name="SimpleMenuExtension::Menu",
                label="Sync with Kumo",
                tip="Auto Sync"
            )

            # iterate through all clouds and add the user cloud names to submenu
            clouds = self.__import_clouds()
            self.lgr.debug("------------------------------------------------------------------------------------------------------")
            self.lgr.debug(str(clouds) + " and size: " +str(len(clouds)))
            # make array of submenu object of lenght equal to number of clouds #IMP CODE to create array of class objects
            submenu = Nautilus.Menu()
            item.set_submenu(submenu)
            
            self.lgr.debug("submenu: " + str(submenu))
            # array of sub_menuitems
            sub_menuitem = [None]*len(clouds)
            self.lgr.debug("sub_menuitem: " + str(sub_menuitem))

            # counter for submenu variable
            submenu_counter = 0
            self.lgr.debug("count outside: " + str(submenu_counter))

            for cloud in clouds:
                # adding submenu
                self.lgr.debug(str(cloud))

                # added menu item
                sub_menuitem[submenu_counter] = Nautilus.MenuItem(
                                            name='SimpleMenuExtension::SubMenu_' + cloud["user_cloud_name"], 
                                            label=cloud["user_cloud_name"] + " (" + cloud["name"] +")" , 
                                            tip='User Cloud'
                                        )
                submenu.append_item(sub_menuitem[submenu_counter])

                sub_menuitem[submenu_counter].connect('activate', self.menu_activate_cb, file, cloud)

                # increment submenu_counter for next value
                submenu_counter += 1
                self.lgr.debug("count inside: " + str(submenu_counter))

            # ----------------- test portion -------------------------
            # adding submenu
            # submenu_counter = 0
            
            # self.lgr.debug("clouds[0] " + str(clouds[0]))

            # # added menu item
            # sub_menuitem[submenu_counter] = Nautilus.MenuItem(
            #                             name='SimpleMenuExtension::SubMenu_' + clouds[0]["user_cloud_name"], 
            #                             label=clouds[0]["user_cloud_name"] + " (" + clouds[0]["name"] +")" , 
            #                             tip='User Cloud'
            #                         )
            # submenu.append_item(sub_menuitem[submenu_counter])

            # sub_menuitem[submenu_counter].connect('activate', self.menu_activate_cb, file, clouds[0])

            # --------------------------------------------------------
            self.lgr.debug("count outside after for: " + str(submenu_counter))

        return [item]
