import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.sql.PreparedStatement;
public class dbread_method {
//*************************
//該function主要功能為將line匯出的聊天室txt檔案中指定目標的對話紀錄整理後傳入db中
//參數一:targetPerson 為指定目標的line id
//參數二:filename 為txt檔案的檔名
//*************************
    public void dbread_method_api(String targetPerson,String filename){
        String host = "140.127.220.89"; 
        int port = 5432; 
        String databaseName = "postgres"; 
        String user = "postgres"; 
        String password = "CrownRu";
        Connection connection = null;
        PreparedStatement preparedStatement = null;
        String currentDate = null; // 存當前日期
        int lineCount = 0;
        
        List<String> targetPersonMessages = new ArrayList<>(); 
        try{
            String line;
            String currentMessage = "";
            // URL
            String url = "jdbc:postgresql://" + host + ":" + port + "/" + databaseName;

            // PostgreSQL JDBC
            Class.forName("org.postgresql.Driver");

            connection = DriverManager.getConnection(url, user, password);
            BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(filename), "UTF-8"));
            while ((line = br.readLine()) != null) {
                lineCount++;
                line = line.trim();
                if (lineCount <= 2) {
                    // 跳過前兩行
                    continue;
                }
                if(line.isEmpty()){
                    continue;
                }

                //if(lineCount<=50){
                    //String line2 = line.replaceAll("\\s+", " ").trim();
                    //Pattern pattern = Pattern.compile(".*" + Pattern.quote(targetPerson.trim()) + ".*");
                    //if (pattern.matcher(line2).matches()) {
                        //System.out.println("Matched: " + line2);
                    //}
                //}

                // 檢查是否為日期行
                line=line.replaceAll("\\t", " ").trim();
                String[] sentence_spilit=line.split(" ");
                //System.out.println(sentence_spilit[1]);

                Pattern datePattern = Pattern.compile("\\d{4}/\\d{2}/\\d{2},\\s+\\w+");  //日期格式
                Matcher dateMatcher = datePattern.matcher(line);
                if (dateMatcher.find()) {
                    currentDate = dateMatcher.group().replaceAll(",\\s+\\w+", ""); // 提取日期部分，去除逗? ","
                    System.out.println("date line:"+currentDate);
                    
                } else if (line.contains(targetPerson) && targetPerson.equals(sentence_spilit[1])) {//去掉前面時間看開頭是不是目標名字
                    // 
                    //System.out.println("hithithithithithithithit");
                    if (line.substring(line.indexOf(targetPerson)).trim().startsWith(targetPerson)){
                        String time = line.substring(0, 5);
                        String message = line.substring(line.indexOf(targetPerson) + targetPerson.length()).trim();

                        System.out.println(line.substring(line.indexOf(targetPerson)).trim());
                        currentMessage = currentDate + " " + time + " " + message; // 构建當前訊息
                        targetPersonMessages.add(currentMessage);
                    }
                } else if (!currentMessage.isEmpty()) {
                    // 
                    Pattern spPattern = Pattern.compile("(\\d{2}:\\d{2})[\\t ]+(.*?)[\\t ]+(.*)");
                    Matcher matcher = spPattern.matcher(line);
                    if (matcher.matches()){
                        continue;
                    }
                    targetPersonMessages.set(targetPersonMessages.size() - 1, targetPersonMessages.get(targetPersonMessages.size() - 1) + line);
                    
                    
                }
                
            }
            String insertSQL = "INSERT INTO \"txt\" (\"txt_content\", \"txt_date\", \"txt_time\") VALUES (?, to_date(?, 'YYYY/MM/DD'), ?::time)ON CONFLICT (\"txt_content\", \"txt_date\", \"txt_time\") DO NOTHING";
            preparedStatement = connection.prepareStatement(insertSQL);

            System.out.println(targetPersonMessages);
            for (String onemessage : targetPersonMessages) {
                String[] parts = onemessage.split(" ", 3);
                String date = parts[0];
                String time = parts[1];
                String content = parts[2];

            
                preparedStatement.setString(1, content);
                preparedStatement.setString(2, date);
                preparedStatement.setString(3, time);
                
                
                preparedStatement.executeUpdate();
            }

            System.out.println("end");

            
            br.close();
        }catch (Exception e) {
            e.printStackTrace();
        }finally {
            try {
                if (preparedStatement != null) {
                    preparedStatement.close();
                }

                if (connection != null) {
                    connection.close();
                }
                
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    
    }
}
