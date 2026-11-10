// Based on the user's shared Korean patch installer template.
// UI coordinates, labels, embedded icon and capsule follow the personal release SOP.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Win32;

internal static class Program
{
    const string GameName = "Sign: Broken Kether";
    const string GameExeName = "SignI.exe";
    const string PlatformAndBuild = "Steam 빌드 26422637";
    const string Version = "v1.0.1";
    const string ExeHash = "F0E95E331D0488C9057DFD1FF720DF1D720438176AF10290FF0F5B0BC807289B";
    const string PayloadHash = "__PAYLOAD_SHA256__";

    [STAThread]
    static int Main(string[] args)
    {
        if (args.Length >= 2 && (args[0] == "/install" || args[0] == "/restore")) {
            try {
                string result = Run(args[1], args[0] == "/restore", delegate(string s) {});
                if (args.Length == 3) File.WriteAllText(args[2], result, Encoding.UTF8);
                return 0;
            } catch (Exception e) {
                if (args.Length == 3) File.WriteAllText(args[2], Redact(e.ToString(), args[1]), Encoding.UTF8);
                return 1;
            }
        }
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new InstallerForm());
        return 0;
    }

    static string Hash(Stream input) {
        using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(input)).Replace("-", "");
    }

    static string Redact(string text, string target) {
        string result = text;
        foreach (var pair in new[] {
            new[] { target.Trim().Trim('"'), "%GAME%" },
            new[] { Path.GetTempPath().TrimEnd('\\','/'), "%TEMP%" },
            new[] { Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "%USERPROFILE%" }
        }) {
            if (!String.IsNullOrEmpty(pair[0]))
                result = Regex.Replace(result, Regex.Escape(pair[0]), delegate(Match m) { return pair[1]; }, RegexOptions.IgnoreCase);
        }
        return result;
    }

    static string ValidateTarget(string path) {
        if (String.IsNullOrWhiteSpace(path)) throw new InvalidOperationException("게임 설치 폴더를 선택해 주세요.");
        string target = Path.GetFullPath(path.Trim().Trim('"')).TrimEnd(Path.DirectorySeparatorChar);
        string exe = Path.Combine(target, GameExeName);
        if (!File.Exists(exe)) throw new InvalidOperationException("선택한 폴더에서 " + GameExeName + "를 찾지 못했습니다.");
        using (var s = File.OpenRead(exe)) {
            if (!Hash(s).Equals(ExeHash, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("지원하지 않는 게임 실행 파일입니다. 지원 빌드와 원본 상태를 확인해 주세요.");
        }
        if (!File.Exists(Path.Combine(target, @"lib\py3-windows-x86_64\python.exe")))
            throw new InvalidOperationException("게임 실행에 필요한 파일이 없습니다. Steam 파일 무결성 검사를 해 주세요.");
        foreach (var p in Process.GetProcessesByName("SignI")) {
            p.Dispose();
            throw new InvalidOperationException("게임이 실행 중입니다. 저장하고 게임을 종료한 뒤 다시 시도해 주세요.");
        }
        return target;
    }

    static void ExtractPayload(string destination) {
        using (var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("payload.zip")) {
            if (stream == null) throw new InvalidDataException("내장 패치 데이터를 찾지 못했습니다.");
            if (!Hash(stream).Equals(PayloadHash, StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("설치기 파일이 손상됐습니다. 배포 ZIP을 다시 받아 주세요.");
            stream.Position = 0;
            string root = Path.GetFullPath(destination) + Path.DirectorySeparatorChar;
            using (var zip = new ZipArchive(stream, ZipArchiveMode.Read)) {
                foreach (var entry in zip.Entries) {
                    if (String.IsNullOrEmpty(entry.Name)) continue;
                    string file = Path.GetFullPath(Path.Combine(destination, entry.FullName.Replace('/', Path.DirectorySeparatorChar)));
                    if (!file.StartsWith(root, StringComparison.OrdinalIgnoreCase) || entry.FullName.Contains(":"))
                        throw new InvalidDataException("내장 파일 경로가 올바르지 않습니다.");
                    Directory.CreateDirectory(Path.GetDirectoryName(file));
                    using (var src = entry.Open()) using (var dst = File.Create(file)) src.CopyTo(dst);
                }
            }
        }
    }

    static string FriendlyError(string raw) {
        if (raw.Contains("Unsupported or modified build")) return "지원 빌드와 원본 파일이 다릅니다. 설치하지 않았습니다.";
        if (raw.Contains("Damaged payload")) return "패치 데이터가 손상됐습니다. 배포 ZIP을 다시 받아 주세요.";
        if (raw.Contains("Patch already installed")) return "기존 패치가 설치되어 있습니다. 먼저 원본 복구를 해 주세요.";
        if (raw.Contains("No active patch")) return "이 설치기의 패치 설치 기록을 찾지 못했습니다.";
        if (raw.Contains("Legacy backup conflict")) return "이전 백업과 현재 백업이 함께 있습니다. 두 폴더를 그대로 보존하고 문의해 주세요.";
        if (raw.Contains("Backup damaged")) return "원본 백업이 손상됐습니다. 백업을 보존하고 문의해 주세요.";
        if (raw.Contains("Files changed after installation")) return "설치 후 변경된 파일이 있습니다. 해당 파일과 백업을 보존해 주세요.";
        if (raw.Contains("PermissionError") || raw.Contains("WinError 5")) return "폴더에 쓰기 권한이 없습니다. 게임 종료 상태와 폴더 권한을 확인해 주세요.";
        return "파일 작업을 완료하지 못했습니다. 오류 로그를 확인해 주세요.";
    }

    static string Run(string selected, bool restore, Action<string> progress) {
        string target = ValidateTarget(selected);
        string tempRoot = Path.GetFullPath(Path.GetTempPath()).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
        string temp = Path.Combine(tempRoot, "SignKoreanPatch_" + Guid.NewGuid().ToString("N"));
        string logFolder = Path.Combine(tempRoot, "SignKoreanPatch_Logs");
        Directory.CreateDirectory(logFolder);
        string logPath = Path.Combine(logFolder, DateTime.Now.ToString("yyyyMMdd_HHmmss_fff") + (restore ? "_restore.log" : "_install.log"));
        try {
            progress("내장 패치 파일을 확인하고 있습니다...");
            Directory.CreateDirectory(temp); ExtractPayload(temp);
            string py = Path.Combine(target, @"lib\py3-windows-x86_64\python.exe");
            var info = new ProcessStartInfo(py, "-B -u \"" + Path.Combine(temp, @"tools\install.py") + "\" " + (restore ? "uninstall" : "install") + " \"" + target + "\"");
            info.WorkingDirectory = target; info.UseShellExecute = false; info.CreateNoWindow = true;
            info.RedirectStandardOutput = true; info.RedirectStandardError = true;
            info.StandardOutputEncoding = Encoding.UTF8; info.StandardErrorEncoding = Encoding.UTF8;
            info.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8";
            info.EnvironmentVariables["PYTHONDONTWRITEBYTECODE"] = "1";
            using (var log = new StreamWriter(logPath, false, new UTF8Encoding(false)))
            using (var process = Process.Start(info)) {
                Task<string> errors = process.StandardError.ReadToEndAsync();
                string line;
                while ((line = process.StandardOutput.ReadLine()) != null) {
                    log.WriteLine(Redact(line, target)); log.Flush();
                    var match = Regex.Match(line, @"^Prepared (\d+) / (\d+)");
                    if (match.Success) progress("적용 파일 준비 중: " + match.Groups[1].Value + " / " + match.Groups[2].Value);
                    else if (line.StartsWith("Checking original")) progress("지원 원본과 패치 파일을 확인하고 있습니다...");
                }
                process.WaitForExit();
                string error = errors.Result; log.Write(Redact(error, target)); log.Flush();
                if (process.ExitCode != 0) throw new InvalidOperationException(FriendlyError(error) + "\r\n\r\n로그: %TEMP%\\SignKoreanPatch_Logs\\" + Path.GetFileName(logPath));
            }
            return restore ? "원본 복구가 완료되었습니다." : "한국어 패치 설치가 완료되었습니다.";
        } finally {
            string full = Path.GetFullPath(temp);
            if (full.StartsWith(tempRoot, StringComparison.OrdinalIgnoreCase) && Path.GetFileName(full).StartsWith("SignKoreanPatch_", StringComparison.Ordinal) && Directory.Exists(full))
                Directory.Delete(full, true);
        }
    }

    static string GuessPath() {
        var roots = new List<string>();
        foreach (string key in new[] {@"HKEY_CURRENT_USER\Software\Valve\Steam", @"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam", @"HKEY_LOCAL_MACHINE\SOFTWARE\Valve\Steam"}) {
            foreach (string name in new[] {"SteamPath", "InstallPath"}) {
                string value = null;
                try { value = Registry.GetValue(key, name, null) as string; }
                catch (System.Security.SecurityException) { }
                catch (UnauthorizedAccessException) { }
                if (!String.IsNullOrEmpty(value)) roots.Add(value);
            }
        }
        roots.Add(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "Steam"));
        var libs = new List<string>(roots);
        foreach (string root in roots) {
            string vdf = Path.Combine(root, @"steamapps\libraryfolders.vdf");
            try {
                if (File.Exists(vdf)) foreach (Match m in Regex.Matches(File.ReadAllText(vdf), "\"path\"\\s+\"([^\"]+)\"")) libs.Add(m.Groups[1].Value.Replace("\\\\", "\\"));
            } catch (IOException) { } catch (UnauthorizedAccessException) { }
        }
        foreach (string lib in libs) {
            string acf = Path.Combine(lib, @"steamapps\appmanifest_3788590.acf");
            if (!File.Exists(acf)) continue;
            var m = Regex.Match(File.ReadAllText(acf), "\"installdir\"\\s+\"([^\"]+)\"");
            if (!m.Success || m.Groups[1].Value.IndexOfAny(new[] {'/', '\\', ':'}) >= 0) continue;
            string candidate = Path.Combine(lib, @"steamapps\common", m.Groups[1].Value);
            if (File.Exists(Path.Combine(candidate, GameExeName))) return candidate;
        }
        return "";
    }

    sealed class InstallerForm : Form
    {
        readonly TextBox path = new TextBox();
        readonly Label status = new Label();
        readonly Button install, restore, browse;
        bool busy;
        public InstallerForm() {
            Text = GameName + " 한국어 패치 " + Version;
            using (var s = Assembly.GetExecutingAssembly().GetManifestResourceStream("InstallerIcon")) Icon = new Icon(s);
            AutoScaleMode = AutoScaleMode.None;
            ClientSize = new Size(640, 285); FormBorderStyle = FormBorderStyle.FixedSingle;
            MaximizeBox = false; MinimizeBox = true; StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(245,245,245); Font = new Font("Malgun Gothic",9F);
            var title = new Label { Text = GameName + "\r\n비공식 한국어 패치", Left=28,Top=22,Width=420,Height=58,Font=new Font("Malgun Gothic",15,FontStyle.Bold) };
            Image logoImage;
            using (var s = Assembly.GetExecutingAssembly().GetManifestResourceStream("InstallerLogo")) using (var img=Image.FromStream(s)) logoImage=new Bitmap(img);
            var logo = new PictureBox { Left=476,Top=19,Width=128,Height=60,SizeMode=PictureBoxSizeMode.Zoom,Image=logoImage,BackColor=Color.Transparent,BorderStyle=BorderStyle.None };
            var info = new Label { Text="지원 게임: " + PlatformAndBuild + " · 원본 파일은 자동 백업됩니다.",Left=28,Top=91,Width=585,Height=24 };
            var folder = new Label { Text="게임 설치 폴더",Left=28,Top=125,Width=150,Height=22 };
            path.SetBounds(28,148,475,25);path.Text=GuessPath();
            browse=new Button { Text="찾아보기",Left=513,Top=146,Width=100,Height=29 };
            browse.Click+=delegate { using (var d=new FolderBrowserDialog()) { d.SelectedPath=path.Text;d.ShowNewFolderButton=false;if(d.ShowDialog(this)==DialogResult.OK)path.Text=d.SelectedPath; } };
            install=new Button { Text="한국어 패치 설치",Left=28,Top=197,Width=178,Height=38,Font=new Font("Malgun Gothic",9,FontStyle.Bold) };
            restore=new Button { Text="원본 복구",Left=218,Top=197,Width=128,Height=38,Font=new Font("Malgun Gothic",9,FontStyle.Bold) };
            install.Click+=delegate { Start(false); };restore.Click+=delegate { Start(true); };
            status.SetBounds(28,245,585,26);status.TextAlign=ContentAlignment.MiddleLeft;status.AutoEllipsis=true;
            Controls.AddRange(new Control[] { title,logo,info,folder,path,browse,install,restore,status });
            // Preserve the shared layout in logical 96-DPI units.
            using (var graphics=CreateGraphics()) {
                float factor=graphics.DpiX/96F;
                if (Math.Abs(factor-1F)>0.01F) {
                    foreach (Control c in Controls) c.SetBounds((int)Math.Round(c.Left*factor),(int)Math.Round(c.Top*factor),(int)Math.Round(c.Width*factor),(int)Math.Round(c.Height*factor));
                    ClientSize=new Size((int)Math.Round(640*factor),(int)Math.Round(285*factor));
                }
            }
            FormClosing+=delegate(object sender,FormClosingEventArgs e) { if(busy)e.Cancel=true; };
        }
        async void Start(bool undo) {
            if(busy)return;
            busy=true; install.Enabled=restore.Enabled=browse.Enabled=path.Enabled=false;
            string selected=path.Text;
            try {
                status.Text="파일 확인 중...";
                string result=await Task.Run(()=>Run(selected,undo,s=>BeginInvoke(new Action(()=>status.Text=s))));
                status.Text=result;
                MessageBox.Show(this,result,"완료",MessageBoxButtons.OK,MessageBoxIcon.Information);
            } catch(Exception e) {
                status.Text="작업을 완료하지 못했습니다.";
                MessageBox.Show(this,Redact(e.Message, selected),"작업 실패",MessageBoxButtons.OK,MessageBoxIcon.Error);
            } finally { busy=false;install.Enabled=restore.Enabled=browse.Enabled=path.Enabled=true; }
        }
    }
}
