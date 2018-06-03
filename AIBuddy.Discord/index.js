const Discord = require('discord.js');
const client = new Discord.Client();

const chalk = require('chalk');
const moment = require('moment');

const config = require("./config.json");

const service = require('./service');
const gm = require('gm')
const path = require('path')
const fs = require('fs');

const timestamp = () => `[${chalk.grey(moment().format('HH:mm:ss'))}]`;

client.on('ready', () => {
  console.log(`${timestamp()} [MASTER]: ${chalk.green('-log')} AI Buddy has started!`);
  client.user.setActivity(`Serving ${client.guilds.size} servers`);
});

client.on('message', async message => {
  if (message.author.bot) return;
  if (message.content.indexOf(config.prefix) !== 0) return;

  const args = message.content.slice(config.prefix.length).trim().split(/ +/g);
  const command = args.shift().toLowerCase();

  if (command === 'reco') {
    
    const attach = message;
    let finalUrl;
    attach.attachments.forEach(element => {
      finalUrl = element.url;
    });

    let result = (await service.postImage(finalUrl));
    console.log(`${timestamp()} [SERVICE]: ${chalk.green('-log')} ${JSON.stringify(result)}`);

    const text = { 
      "minusvalido": result.minusvalido,
      "no_minusvalido": result.no_minusvalidos
    };

    gm(path.join(process.cwd(), 'res', 'images', 'base.png'))
      .font(path.join(process.cwd(), 'res', 'fonts', 'animeace.ttf'), 36)
      .gravity('Center')
      .fill('#ffffff')
      .stroke('black', 2)
      .drawText(110, 25, text.minusvalido)
      .drawText(110, 85, text.no_minusvalido)
      .write('reco.png', (err) => {
        if (err) {
          console.error(`${timestamp()} [SERVICE]: ${chalk.red('-error')} ${err}`);
          return;
        }
        return message.channel.send({
          files: [
            "reco.png"
          ]
        });
      });

  }

});

client.login(config.token);