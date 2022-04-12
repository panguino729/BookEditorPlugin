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

namespace BookEditorTool
{
    public partial class Form1 : Form
    {
        public FontFamily[] Families { get; }

        public Form1()
        {
            InitializeComponent();

            // Source: https://stackoverflow.com/questions/5155049/toolstripcombobox-set-font-style by Hans Passant
            ComboBox box = (ComboBox)fontComboBox.Control;
            box.DrawMode = DrawMode.OwnerDrawVariable;

            // Source: https://stackoverflow.com/questions/46037189/how-to-make-a-font-combobox-in-c by Fabio
            box.DrawItem += fontComboBox_DrawItem;
            box.DataSource = System.Drawing.FontFamily.Families.ToList();
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
                saveFileDialog1.FileName = openFiles.Items[0].ToString();
                saveFileDialog1.DefaultExt = "rtf";
                saveFileDialog1.Filter = "Rich Text Format|*.rtf";

                if (saveFileDialog1.ShowDialog() == DialogResult.OK)
                {
                    TextEditField.SaveFile(saveFileDialog1.FileName);
                }
            }
            catch (Exception errorMsg)
            {
                MessageBox.Show(errorMsg.Message);
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
