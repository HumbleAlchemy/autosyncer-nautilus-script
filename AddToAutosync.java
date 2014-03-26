
import java.io.File;
import java.io.IOException;
import java.net.MalformedURLException;


// This main method is called when a folder is added to autosync 
public class AddToAutosync {
	public static void main(String args[]) {
		// args0 = cloud name
		// args1 = usercloudID
		// args2 = folderPath
		if (args.length == 0) {
			System.out
					.println("Argument not passed, arg1 should be name of the directory");
			System.exit(-1);
		}
		try {
			File folder = new File(args[2]);
			String folderPathOnServer = "/" + folder.getName();
			EventHandler.createFolder(args[0], args[1], folderPathOnServer);
			for (File child : folder.listFiles()) {
				EventHandler.upload(args[0], args[1], folderPathOnServer,
						child.getAbsolutePath());
			}

		} catch (MalformedURLException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}

	}
}

