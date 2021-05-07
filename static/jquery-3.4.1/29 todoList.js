$(function(){
	//模拟数据
	// var todoList = [
	// 	{title:'派大星', done:false},
	// 	{title:'海绵宝宝', done:false},
	// 	{title:'章鱼哥', done:false},
	// 	{title:'蟹老板', done:true},
	// 	{title:'痞老板', done:true},
	// ]


	//加载数据方法
	function loadData(){
		var collection = localStorage.getItem('todo');
		if(collection){
			return JSON.parse(collection);
		}else{
			return [];
		}
	}

	//保存数据方法
	function saveData(data){
		localStorage.setItem('todo',JSON.stringify(data));
	}

	//删除数据方法
	// function removeData(data,i){
	// 	localStorage.removeItem('data[i]');
	// }




	//加载网页数据
	load();
	function load(){
		var todoCount = 0;
		var doneCount = 0;
		var todoStr = '';
		var doneStr = '';
		var todoList = loadData();
		if(todoList && todoList.length > 0){
			//有数据
			todoList.forEach(function(data,i){
				if(data.done){
					//已经完成
					doneStr += `
						<li>
							<input type="checkbox" index="${i}" checked="checked">
							<p id="p-${i}" index=${i}>${data.title}</p>
							<a href="javascript:;">-</a>
						</li>
					`;
					doneCount++;
				}else{
					//正在进行
					todoStr += `
						<li>
							<input type="checkbox" index="${i}">
							<p id="p-${i}" index=${i}>${data.title}</p>
							<a href="javascript:;">-</a>
						</li>
					`;
					todoCount++;
				}

				$('#donelist').html(doneStr);
				$('#todolist').html(todoStr);
				$('#todocount').html(todoCount);
				$('#donecount').html(doneCount);
			})
			
		}else{
			//无数据
			$('#todolist').html('');
			$('#donelist').html('');
			$('#todocount').html(todoCount);
			$('#donecount').html(doneCount);
		}
	}




	//添加数据的方法
	//输入框/监听键盘输入
	$('#title').keydown(function(event){
		// console.log(event.keyCode);
		if(event.keyCode === 13){
			//获取输入框的值
			var val = $(this).val();
			if(!val){
				alert('请输入值');
			}else{
				var todoList = loadData();
				todoList.unshift({
					title:val,
					done:false
				});

				//清空输入框的值
				$(this).val('');
				saveData(todoList);
				load();
			}
		}
	})




	//使用事件代理的方法进行删除操作
	//事件代理：把事件加到父级上，触发执行效果
	$('#todolist').on('click','a',function(){
		//获取a标签的父级li的索引
		var i2 = $(this).parent().index();
		var todoList = loadData();
		console.log(todoList);
		//利用数组的方法进行删除操作
		//从索引 i 开始删除 1 个
		removeData(todoList,i2);
		load();
	})




	//更新数据
	//事件代理：监听复选框改变事件
	$('#todolist').on('change','input[type=checkbox]',function(){
		//将每条复选框的index值变成数值类型拿出来
		var i1 = parseInt($(this).attr('index'));
		//使用函数方法,更新数据
		//（索引，需要改变的key，改变的value）
		update(i1,'done',true);
	})

	$('#donelist').on('change','input[type=checkbox]',function(){
		//将每条复选框的index值变成数值类型拿出来
		var i1 = parseInt($(this).attr('index'));
		//使用函数方法,更新数据
		//（索引，需要改变的key，改变的value）
		update(i1,'done',false);
	})
	//update方法
	function update(i1,key,value){
		var todoList = loadData();
		//将todoList数组进行切分(从i1开始，切一个)再拿出第1(索引0)个
		var todo = todoList.splice(i1,1)[0];
		//改变 done 的值
		todo[key] = value;
		//将新值替换进去
		todoList.splice(i1,0,todo);
		saveData(todoList);

		load();
	}





	//编辑操作
	$('#todolist').on('click','p',function(){
		var i = $(this).parent().index();
		var title = $(this).html();
		//防止与下面的this冲突
		var $p = $(this);
		$p.html(`<input type="text" id='input-${i}' value=${title}>`)
		//设置内容选中的长度
		$(`#input-${i}`)[0].setSelectionRange(0,$(`#input-${i}`).val().length);
		//获取焦点
		$(`#input-${i}`).focus();

		//时区焦点，保存更改的数据
		$(`#input-${i}`).blur(function(){
			//判断是否有值
			if($(this).val().length === 0){
				//如果没有值，那p拿回原来的值
				$p.html(title);
				alert('输入的内容不能为空');
			}else{
				//调用函数更新数据
				update(i,'title',$(this).val());
			}
		})
	})	






 



})



