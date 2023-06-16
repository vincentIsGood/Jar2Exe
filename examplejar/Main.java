// Compile   : javac Main.java
// Create jar: jar cvfm example.jar Manifest.txt Main.class

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class Main{
    public static void main(String[] args) throws IOException {
        if(args.length > 0 && args[0].equals("--help")){
            System.out.println("No help for you!");
            return;
        }
        System.out.println("Current root dir: " + new File(".").getCanonicalPath());
        System.out.println("Seems like you found a way to run this. Congrats.");
        System.out.println("Content of test.txt: " + Files.readString(Path.of("./data/test.txt")));
    }
}