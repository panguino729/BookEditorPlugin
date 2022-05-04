using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;
using System.Diagnostics;

namespace BookEditorTool
{
    public partial class Form1 : Form
    {
        public FontFamily[] Families { get; }

        private string orgBookPath = "";
        private string bookFilepath = "";
        private string bookFilenameImported = "";
        private bool cmdOpen = false;
        private MemoryStream userInput;

        public Form1()
        {
            InitializeComponent();

            // Source: https://stackoverflow.com/questions/5155049/toolstripcombobox-set-font-style by Hans Passant
            ComboBox box = (ComboBox)fontComboBox.Control;
            box.DrawMode = DrawMode.OwnerDrawVariable;

            // Source: https://stackoverflow.com/questions/46037189/how-to-make-a-font-combobox-in-c by Fabio
            box.DrawItem += fontComboBox_DrawItem;
            box.DataSource = System.Drawing.FontFamily.Families.ToList();

            // Source: https://www.howtogeek.com/howto/programming/get-command-line-arguments-in-a-windows-forms-application/
            string[] args = Environment.GetCommandLineArgs();

            int count = 0;

            // Declare a new memory stream.
            userInput = new MemoryStream();

            // CMD: <BookEditorTool.exe filepath> open <book name>
            foreach (string arg in args)
            {
                if (args[count] == "open")
                {
                    cmdOpen = true;
                    System.Diagnostics.Process.Start("calibre", " -s");
                    orgBookPath = args[count + 1];
                    bookFilepath = Path.GetDirectoryName(args[count + 1]);
                    bookFilenameImported = Path.GetFileName(args[count + 1]);
                    TextEditField.LoadFile(args[count + 1], RichTextBoxStreamType.RichText);
                    openFiles.Items.Clear();
                    openFiles.Items.Add(args[count + 2]);
                }

                count++;
            }
        }

        /// <summary>
        /// Save File
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void toolStripButton1_Click(object sender, EventArgs e)
        {
            try
            {
                if (cmdOpen)
                {
                    saveFileDialog1.FileName = bookFilenameImported;
                }
                else
                {
                    saveFileDialog1.FileName = openFiles.Items[0].ToString();
                }

                saveFileDialog1.CreatePrompt = true;
                saveFileDialog1.OverwritePrompt = true;
                saveFileDialog1.InitialDirectory = bookFilepath;
                saveFileDialog1.DefaultExt = "rtf";
                saveFileDialog1.Filter = "Rich Text Format|*.rtf";

                //bookFilepath = Path.GetDirectoryName(bookFilepath);

                Stream fileStream;

                TextEditField.SaveFile(userInput, RichTextBoxStreamType.RichText);
                userInput.WriteByte(13);

                if (saveFileDialog1.ShowDialog() == DialogResult.OK)
                {
                    //TextEditField.SaveFile(saveFileDialog1.FileName);

                    // Open the file, copy the contents of memoryStream to fileStream,
                    // and close fileStream. Set the memoryStream.Position value to 0 
                    // to copy the entire stream. 
                    fileStream = saveFileDialog1.OpenFile();
                    userInput.Position = 0;
                    userInput.WriteTo(fileStream);
                    fileStream.Close();

                    if (cmdOpen)
                    {
                        // Source: https://www.codeproject.com/Questions/173331/CMD-from-Windows-Form
                        string convertCmd = string.Format("ebook-convert \"{0}\" \"{1}\"", orgBookPath, Path.ChangeExtension(orgBookPath, "epub")); // input file, output file

                        Process process = new Process();
                        ProcessStartInfo processtartinfo = new ProcessStartInfo();
                        processtartinfo.Arguments = convertCmd;
                        processtartinfo.WindowStyle = ProcessWindowStyle.Hidden;
                        processtartinfo.FileName = "CMD.exe";

                        process.StartInfo = processtartinfo;
                        process.Start();

                        System.Diagnostics.Process.Start("calibre");

                        TextEditField.Text = convertCmd;
                    }

                    //Application.Exit();
                }
            }
            catch (Exception errorMsg)
            {
                MessageBox.Show(errorMsg.Message);
            }
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (cmdOpen)
            {
                // Source: https://www.codeproject.com/Questions/173331/CMD-from-Windows-Form
                string convertCmd = string.Format("ebook-convert {0} {1}", bookFilepath, Path.ChangeExtension(bookFilepath, "rtf")); // input file, output file

                ProcessStartInfo processtartinfo = new ProcessStartInfo();
                processtartinfo.Arguments = convertCmd;
                processtartinfo.WindowStyle = ProcessWindowStyle.Hidden;
                processtartinfo.FileName = "CMD.exe";
                System.Diagnostics.Process.Start(processtartinfo);

                System.Diagnostics.Process.Start("calibre");
            }
        }

        private void toolStripButton2_Click(object sender, EventArgs e)
        {

        }

        private void listBox1_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void richTextBox1_TextChanged(object sender, EventArgs e)
        {

        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void toolStripComboBox1_Click(object sender, EventArgs e)
        {

        }

        #region Fonts - Source: https://stackoverflow.com/questions/46037189/how-to-make-a-font-combobox-in-c by Fabio
        private void fontComboBox_DrawItem(object sender, DrawItemEventArgs e)
        {

            var comboBox = (ComboBox)sender;
            var fontFamily = (FontFamily)comboBox.Items[e.Index];
            var font = new Font(fontFamily, comboBox.Font.SizeInPoints);

            e.DrawBackground();
            e.Graphics.DrawString(font.Name, font, Brushes.Black, e.Bounds.X, e.Bounds.Y);
        }

        public void fontComboBox_SelectedIndexChanged(object sender, EventArgs e)
        {
            fontTextBoxNameTest.Text = ((FontFamily)fontComboBox.SelectedItem).Name;
            fontComboBox.Text = ((FontFamily)fontComboBox.SelectedItem).Name;
            TextEditField.SelectionFont = new Font((FontFamily)fontComboBox.SelectedItem, TextEditField.Font.Size);
        }
        #endregion

        public void fontSizeComboBox_SelectedIndexChanged(object sender, EventArgs e)
        {
            TextEditField.SelectionFont = new Font(fontComboBox.SelectedItem.ToString(), float.Parse(fontSizeComboBox.SelectedItem.ToString()));
        }

        /// <summary>
        /// Open file
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void toolStripButton2_Click_1(object sender, EventArgs e)
        {
            try
            {
                if (openFileDialog1.ShowDialog() == DialogResult.OK)
                {
                    TextEditField.LoadFile(openFileDialog1.FileName, RichTextBoxStreamType.RichText);
                    openFiles.Items.Clear();
                    openFiles.Items.Add(openFileDialog1.SafeFileName);
                }
            }
            catch (Exception errorMsg)
            {
                MessageBox.Show(errorMsg.Message);
            }

        }

        private void openFileDialog1_FileOk(object sender, CancelEventArgs e)
        {

        }

        private void toolStrip1_ItemClicked(object sender, ToolStripItemClickedEventArgs e)
        {

        }

        /// <summary>
        /// Toggle Bold
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void toolStripButton3_Click(object sender, EventArgs e)
        {
            if (TextEditField.SelectionFont != null)
            {
                System.Drawing.Font currentFont = TextEditField.SelectionFont;
                System.Drawing.FontStyle newFontStyle;

                if (TextEditField.SelectionFont.Bold == true)
                {
                    boldButton.Checked = false;
                    newFontStyle = FontStyle.Regular;
                }
                else
                {
                    boldButton.Checked = true;
                    newFontStyle = FontStyle.Bold;
                }

                TextEditField.SelectionFont = new Font(currentFont.FontFamily, currentFont.Size, newFontStyle);
            }
        }

        /// <summary>
        /// Toggle Italics
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void toolStripButton4_Click(object sender, EventArgs e)
        {
            if (TextEditField.SelectionFont != null)
            {
                System.Drawing.Font currentFont = TextEditField.SelectionFont;
                System.Drawing.FontStyle newFontStyle;

                if (TextEditField.SelectionFont.Italic == true)
                {
                    italicButton.Checked = false;
                    newFontStyle = FontStyle.Regular;
                }
                else
                {
                    italicButton.Checked = true;
                    newFontStyle = FontStyle.Italic;
                }

                TextEditField.SelectionFont = new Font(currentFont.FontFamily, currentFont.Size, newFontStyle);
            }
        }

        /// <summary>
        /// Toggle Underline
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void toolStripButton5_Click(object sender, EventArgs e)
        {
            if (TextEditField.SelectionFont != null)
            {
                System.Drawing.Font currentFont = TextEditField.SelectionFont;
                System.Drawing.FontStyle newFontStyle;

                if (TextEditField.SelectionFont.Underline == true)
                {
                    underlineButton.Checked = false;
                    newFontStyle = FontStyle.Regular;
                }
                else
                {
                    underlineButton.Checked = true;
                    newFontStyle = FontStyle.Underline;
                }

                TextEditField.SelectionFont = new Font(currentFont.FontFamily, currentFont.Size, newFontStyle);
            }
        }

        private void saveFileDialog1_FileOk(object sender, CancelEventArgs e)
        {

        }
    }
}
