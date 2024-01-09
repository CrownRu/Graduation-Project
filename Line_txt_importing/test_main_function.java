//*************************
//該檔案為dbread_method的主程式測試檔案
//*************************
public class test_main_function {
    public static void main(String[] args){
        String filename="linechat.txt";
        String targetPerson = "目標人物line_id";
        dbread_method caller=new dbread_method();
        caller.dbread_method_api(targetPerson,filename);
    }
}
